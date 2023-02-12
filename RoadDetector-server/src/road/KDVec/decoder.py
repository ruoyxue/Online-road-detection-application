import torch
import torch.nn.functional as F
import copy
import numpy as np
import math



class Decoder:
    """ used to transform features to detection results """
    @staticmethod
    def keypoint_decode(loc, direction, max_keypoint=350, nms_poolsize=3, loc_threshold=0.5, dir_threshold=0.5):
        """
        Decode output feature map to keypoint results

        Notes:
            loc: (batch, 1, height, width)
            direction: (batch, 18, height, width)

        Args:
            max_keypoint: select top k features in loc
            loc_threshold: threshold for determining low confidence location
            dir_threshold: threshold for determining low direction location
        """
        batch, _, height, width = loc.shape
        loc = loc.cpu()
        direction = direction.cpu()

        loc = KeyPointDecoder.pseudo_nms(loc, pool_size=nms_poolsize)
        scores, index, ys, xs = KeyPointDecoder.topk_score(loc, max_keypoint)
        location = torch.zeros(batch, max_keypoint, 2)

        # remove low confidence keypoints
        row, col = torch.where(scores < loc_threshold)
        ys[[row, col]], xs[[row, col]] = -1, -1
        location[:, :, 0] = xs
        location[:, :, 1] = ys

        direction = KeyPointDecoder.gather_feature(direction, index, use_transform=True)
        direction = direction.reshape(batch, max_keypoint, 6, 3)

        # normalise direction vector
        length = torch.clamp(torch.sqrt(direction[:, :, :, 1] ** 2 + direction[:, :, :, 2] ** 2), 1e-8)
        direction[:, :, :, 1] /= length
        direction[:, :, :, 2] /= length

        # remove low confidence direction
        direction[direction[:, :, :, 0] < dir_threshold] = 0

        return location.int(), direction  # location (batch, max_keypoint, 2), direction (batch, max_keypoint, 6, 3)

    @staticmethod
    def vectorization_decode_greedy(location, direction, lambda_angle_dist, lambda_point_line_dist,
                                    dir_offset_range, point_line_distance_range, loc_range, max_pending_distance,
                                    lambda_loc_range, loc_range_for_lambda_loc):
        """
        Decode locations and directions to adjacency matrix using greedy algorithm

        Notes:
            location: (batch, max_keypoint, 2)
            direction: (batch, max_keypoint, 6, 3)

        Args:
            distance_range: distance range for criterion adjustment
            point_line_distance: distance range between one keypoint and other matched keypoint's direction

        Returns:
            adjacency matrix of locations
        """
        assert location.shape[:2] == direction.shape[:2]
        locations = location.float()
        directions = copy.deepcopy(direction)
        batch_size, max_keypoint = location.shape[:2]

        adjacency_matrix = torch.zeros(batch_size, max_keypoint, max_keypoint)
        for batch in range(batch_size):
            adjacency_matrix[batch, :, :] = VectorizationDecoder.calculate_adjacency_matrix_greedy(
                location=locations[batch], direction=directions[batch],
                lambda_angle_dist=lambda_angle_dist, lambda_point_line_dist=lambda_point_line_dist,
                dir_offset_range=dir_offset_range, point_line_distance_range=point_line_distance_range,
                loc_range=loc_range, max_pending_distance=max_pending_distance,
                lambda_loc_range=lambda_loc_range, loc_range_for_lambda_loc=loc_range_for_lambda_loc
            )

        return adjacency_matrix.int()


class KeyPointDecoder:
    @staticmethod
    def pseudo_nms(fmap, pool_size=3):
        """
        Apply max pooling to get the same effect of nms

        Args:
            fmap(Tensor): output tensor of previous step
            pool_size(int): size of max-pooling
        """
        pad = (pool_size - 1) // 2
        fmap_max = F.max_pool2d(fmap, pool_size, stride=1, padding=pad)
        keep = (fmap_max == fmap).float()
        return fmap * keep

    @staticmethod
    def topk_score(scores, k=50):
        """ get top K point in score map """
        batch, channel, height, width = scores.shape

        # get topk score and its index in every H x W(channel dim) feature map
        topk_score, topk_index = torch.topk(scores.reshape(batch, channel, -1), k)  # (batch, channel, K)
        topk_index = topk_index % (height * width)  # (batch, channel, K)
        topk_ys = (topk_index / width).int().float()  # (batch, channel, K)
        topk_xs = (topk_index % width).int().float()  # (batch, channel, K)

        return topk_score.reshape(batch, k), topk_index.reshape(batch, k), \
               topk_ys.reshape(batch, k), topk_xs.reshape(batch, k)

    @staticmethod
    def gather_feature(feature_map, index, mask=None, use_transform=False):
        if use_transform:
            # change a (N, C, H, W) tenor to (N, HxW, C) shape
            batch, channel = feature_map.shape[:2]
            feature_map = feature_map.reshape(batch, channel, -1).permute((0, 2, 1))

        dim = feature_map.size(-1)
        index = index.unsqueeze(len(index.shape)).expand(*index.shape, dim)
        feature_map = feature_map.gather(dim=1, index=index)
        if mask is not None:
            # this part is not called in Res18 dcn COCO
            mask = mask.unsqueeze(2).expand_as(feature_map)
            feature_map = feature_map[mask]
            feature_map = feature_map.reshape(-1, dim)
        return feature_map

    @staticmethod
    def find_endpoints(skeleton, coordinates):
        """
        Find endpoints in coordinates

        Notes:
            skeleton: (height, width)
            coordinates: [(y1, x1), (y2, x2)....]
        """
        skeleton = skeleton > 0
        height, width = skeleton.shape
        endpoints = []
        offset_pairs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

        for (y, x) in coordinates:
            neighbor_count = 0
            for (m, n) in offset_pairs:
                y_new, x_new = y + m, x + n
                if 0 <= y_new < height and 0 <= x_new < width:
                    if skeleton[y_new, x_new] == 1:
                        neighbor_count += 1
            if neighbor_count == 1:
                endpoints.append([y, x])

        return endpoints


class VectorizationDecoder:
    @staticmethod
    def calculate_adjacency_matrix_greedy(
            location, direction, lambda_angle_dist, lambda_point_line_dist,
            dir_offset_range, point_line_distance_range, loc_range, max_pending_distance,
            lambda_loc_range, loc_range_for_lambda_loc
    ):
        """
        Calculate adjacency matrix according to location and direction, using Greedy Algorithm

        Args:
            location (torch.Tensor): (max_keypoint, 2)
            direction (torch.Tensor): (max_keypoint, 6, 3)

        Returns:
            adjacency_matrix of these keypoints
        """
        assert location.shape[0] == direction.shape[0]
        max_keypoint = location.shape[0]
        adjacency_matrix = torch.zeros(max_keypoint, max_keypoint)
        num_valid_keypoint = torch.all(location >= 0, dim=1).sum()

        # First, we have to save all the direction info in a list and each dir as a tuple
        # (location, direction, sec_dix, loc_idx)
        single_dir_info_list = []
        for loc_idx in range(num_valid_keypoint):
            for dir_idx in range(6):
                if direction[loc_idx, dir_idx, 0] > 0:
                    dir_angle = VectorizationDecoder.get_degree(
                        direction[loc_idx, dir_idx, 1], direction[loc_idx, dir_idx, 2]
                    )
                    sec_idx = int(dir_angle) // 60
                    single_dir_info = (location[loc_idx], direction[loc_idx, dir_idx, 1:], sec_idx, loc_idx)
                    single_dir_info_list.append(single_dir_info)

        # Next, we try to pick out all the possible edges (two direction could form an edge)
        dir_count = len(single_dir_info_list)
        cost_matrix = np.full((dir_count, dir_count), 1000.)
        for i in range(dir_count):
            current_dir_info = single_dir_info_list[i]
            possible_matching_sec_list = \
                [(current_dir_info[2] + 2) % 6, (current_dir_info[2] + 3) % 6, (current_dir_info[2] + 4) % 6]
            for j in range(i + 1, dir_count):
                # if True:
                if single_dir_info_list[j][2] in possible_matching_sec_list:
                    # we only take adjacent section idx as possible sections
                    to_match_dir_info = single_dir_info_list[j]
                    if torch.all(to_match_dir_info[0] == current_dir_info[0]):
                        # we don't let two directions of same keypoint to be matched
                        continue
                    # we calculate distance of two directions to judge whether to match
                    distance = VectorizationDecoder.calculate_distance_of_two_directions(
                        dir_info1=current_dir_info, dir_info2=to_match_dir_info,
                        lambda_angle_dist=lambda_angle_dist, lambda_point_line_dist=lambda_point_line_dist,
                        dir_offset_range=dir_offset_range, point_line_distance_range=point_line_distance_range,
                        loc_range=loc_range, lambda_loc_range=lambda_loc_range,
                        loc_range_for_lambda_loc=loc_range_for_lambda_loc
                    )
                    if distance <= max_pending_distance:
                        cost_matrix[i, j] = distance
                        cost_matrix[j, i] = distance

        # Finally, use Greedy Algorithm to compute the best matching strategy
        match_output = VectorizationDecoder.greedy(cost_matrix)
        for dir_idx_1, dir_idx_2 in match_output:
            loc_idx1 = single_dir_info_list[dir_idx_1][3]
            loc_idx2 = single_dir_info_list[dir_idx_2][3]
            assert loc_idx1 != loc_idx2
            adjacency_matrix[loc_idx1, loc_idx2] = 1
            adjacency_matrix[loc_idx2, loc_idx1] = 1

        return adjacency_matrix

    
    @staticmethod
    def greedy(cost_matrix):
        """
        Find pairs with lowest cost using greedy algorithm
        Args:
            cost_matrix (np.ndarray): input cost matrix, 1000 denotes invalid value

        Returns:
            match_pairs (List(Tuple(int, int))): best matching pairs
        """
        match_pairs = []
        if len(cost_matrix) > 0:
            lowest_value = np.min(cost_matrix)
            find_smallest = lambda arr: np.unravel_index(np.argmin(arr), arr.shape)
            while lowest_value < 1000:
                idx1, idx2 = find_smallest(cost_matrix)
                match_pairs.append((idx1, idx2))
                cost_matrix[idx1, :] = 1000
                cost_matrix[idx2, :] = 1000
                cost_matrix[:, idx1] = 1000
                cost_matrix[:, idx2] = 1000
                lowest_value = np.min(cost_matrix)

        return match_pairs


    @staticmethod
    def argsort_matrix(matrix, descending=False):
        """
        Give a matrix, get the sorted coordinate (min->max or max->min)

        Notes:
            matrix: (height, width)

        Args:
            descending: False means min --> max, True means max --> min
        """
        height, width = matrix.shape
        flat_sort = torch.argsort(matrix.flatten(), descending=descending)
        coord_width = flat_sort % width
        coord_height = torch.div(flat_sort, width, rounding_mode='trunc')
        return torch.stack([coord_height, coord_width], dim=1)

    @staticmethod
    def get_unit_vector(start_loc, end_loc):
        """
        Compute unit vector.

        Notes:
            start_loc: (2)
            end_loc: (2)
        """
        return (end_loc.float() - start_loc) / torch.clamp(torch.norm(end_loc.float() - start_loc), min=1e-8)

    @staticmethod
    def get_angle_between_two_vectors(vec1, vec2):
        """
        Compute angle between two vector, [0, 180].

        Notes:
            vec1: (2)
            vec2: (2)
        """
        cos_theta = torch.sum(vec1 * vec2) / torch.clamp(torch.norm(vec1) * torch.norm(vec2), min=1e-8)
        # must clamp cos_theta to avoid float error!!!
        cos_theta = torch.clamp(cos_theta, min=-1., max=1.)
        degree = torch.rad2deg(torch.arccos(cos_theta))
        return degree

    @staticmethod
    def get_point_line_distance(point_loc, dir_loc, dir):
        """ Compute vertical distance between point and dir at dir_loc"""
        c = point_loc - dir_loc
        a = dir
        # len_b = torch.sqrt(torch.clamp(torch.norm(c) ** 2 - (torch.sum(a * c) / torch.norm(a)) ** 2, min=0.))
        len_b = np.linalg.norm(np.cross(c, a) / np.linalg.norm(a))
        if np.dot(c, a) < 0:
            len_b = 10000
        return len_b


    def designed_angle_distance(x, y):
        """ Calculate designed distance between x and y """
        return torch.norm(x + y)

    @staticmethod
    def get_degree(sin_value, cos_value):
        """ get angle in [0, 360) via sin and cos value """
        theta = math.atan2(sin_value, cos_value)
        if theta < 0:
            theta += 2 * math.pi
        return math.degrees(theta)

    @staticmethod
    def calculate_distance_of_two_directions(
            dir_info1, dir_info2, lambda_angle_dist, lambda_point_line_dist,
            dir_offset_range, point_line_distance_range, loc_range, lambda_loc_range,loc_range_for_lambda_loc
    ):
        """
        Compute distance between two directions, used to judge whether can form an edge

        Args:
            dir_info1 (Tuple): (location, direction, sec_dix, loc_idx)
            dir_info2 (Tuple): (location, direction, sec_dix, loc_idx)
            lambda_angle_dist (float): weight of angle distance
            lambda_point_line_dist (float): weight of point line distance
            max_dir_offset (float): threshold for angle
            max_point_line_distance (float): threshold for point line distance
            loc_range (List): 
            lambda_loc_range (float): 

        Returns:
            Designed distance of two directions
        """
        loc1, dir1, _, _ = dir_info1
        loc2, dir2, _, _ = dir_info2

        # unify coordinate system of reference_vec and direction !
        reference_vec1 = VectorizationDecoder.get_unit_vector(start_loc=loc1, end_loc=loc2)
        tem_dir1 = torch.as_tensor([dir1[1], dir1[0]])
        angle1 = VectorizationDecoder.get_angle_between_two_vectors(reference_vec1, tem_dir1)
        point_line_distance1 = VectorizationDecoder.get_point_line_distance(loc2, loc1, tem_dir1)

        reference_vec2 = VectorizationDecoder.get_unit_vector(start_loc=loc2, end_loc=loc1)
        tem_dir2 = torch.as_tensor([dir2[1], dir2[0]])
        angle2 = VectorizationDecoder.get_angle_between_two_vectors(reference_vec2, tem_dir2)
        point_line_distance2 = VectorizationDecoder.get_point_line_distance(loc1, loc2, tem_dir2)

        loc_distance = torch.norm(loc1 - loc2)
        
        if loc_distance <= loc_range[0]:
            max_point_line_distance = point_line_distance_range[0]
            max_dir_offset = dir_offset_range[0]
        elif loc_distance >= loc_range[1]:
            max_point_line_distance = point_line_distance_range[1]
            max_dir_offset = dir_offset_range[1]
        else:
            max_point_line_distance = \
                point_line_distance_range[0] + ((loc_distance - loc_range[0]) / (loc_range[1] - loc_range[0])) * \
                (point_line_distance_range[1] - point_line_distance_range[0])
            max_dir_offset = dir_offset_range[0] + ((loc_distance - loc_range[0]) / (loc_range[1] - loc_range[0])) * \
                (dir_offset_range[1] - dir_offset_range[0])

        if angle1 + angle2 >= max_dir_offset or \
            point_line_distance1 + point_line_distance2 >= max_point_line_distance:
            return 1000

        # we have to compute another coefficient by location distance, where closer is better
        if loc_distance < loc_range_for_lambda_loc[0]:
            lambda_loc = lambda_loc_range[0]
        elif loc_distance > loc_range_for_lambda_loc[1]:
            lambda_loc = lambda_loc_range[1]
        else:
            lambda_loc = lambda_loc_range[0] + ((loc_distance - loc_range_for_lambda_loc[0]) / (loc_range_for_lambda_loc[1] - loc_range_for_lambda_loc[0])) * \
                (lambda_loc_range[1] - lambda_loc_range[0])
            
        distance = (point_line_distance1 + point_line_distance2) * lambda_loc

        return distance

