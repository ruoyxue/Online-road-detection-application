<template>
  <div>
    <el-result
      icon="warning"
      title="404 Not Found"
      sub-title="The page you are looking for has lost"
    >
      <template #extra>
        <el-button type="primary" @click="$router.push('/')">Back to Interface</el-button>
      </template>
    </el-result>
  </div>
</template>
