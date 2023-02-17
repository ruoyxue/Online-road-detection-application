class GlobeVar:
    def __init__(self, value) -> None:
        self.value = value
    
    def set_value(self, value):
        self.value = value
    
    def get_value(self):
        return self.value
    
progress = GlobeVar(0)  # record detection progress
permit = GlobeVar(True)  # record whether need to download or detection
