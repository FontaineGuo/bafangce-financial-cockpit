<template>
  <div class="portfolios">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>投资组合</span>
          <el-button type="primary">创建组合</el-button>
        </div>
      </template>

      <el-empty description="暂无投资组合，点击右上角创建" />
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
