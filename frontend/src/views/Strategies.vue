<template>
  <div class="strategies">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>策略管理</span>
          <el-button type="primary">创建策略</el-button>
        </div>
      </template>

      <el-empty description="暂无策略，点击右上角创建" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
