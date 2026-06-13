<template>
  <div class="history-root">
    <div class="glass-card hist-header-bar">
      <h3 class="hist-title"><v-icon color="green-accent-3" start size="24">mdi-history</v-icon> 诊断历史 ({{ total }} 条)</h3>
      <v-btn v-if="total > 0" variant="tonal" color="green-accent-3" size="small" rounded="lg" prepend-icon="mdi-download" @click="exportExcel">导出 Excel</v-btn>
    </div>

    <div v-if="records.length === 0" class="glass-card hist-empty">
      <v-icon size="48" color="grey-lighten-1">mdi-leaf-off</v-icon>
      <p>暂无诊断记录</p>
      <p class="hist-empty-sub">快去拍张叶片照片吧！</p>
    </div>

    <div v-else class="hist-grid">
      <div v-for="r in records" :key="r.id" class="glass-card hist-card">
        <img v-if="r.image_base64" :src="'data:image/jpeg;base64,' + r.image_base64" class="hist-thumb" />
        <div class="hist-info">
          <div class="hist-disease">{{ r.top1_disease }}</div>
          <div class="hist-date">{{ r.created_at?.slice(0, 16) }}</div>
          <div class="hist-chips">
            <v-chip size="x-small" :color="r.is_healthy ? 'green' : 'red'" pill>{{ r.is_healthy ? '健康' : '病害' }}</v-chip>
            <v-chip v-if="r.severity" size="x-small" variant="tonal" :color="{mild:'green',moderate:'orange',severe:'red'}[r.severity]" pill class="ml-1">{{ {mild:'轻度',moderate:'中度',severe:'重度'}[r.severity] }}</v-chip>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../../services/api.js';
export default {
  name: 'HistoryTab',
  data() { return { records: [], total: 0 }; },
  mounted() { this.loadHistory(); },
  methods: {
    async loadHistory() { try { const d = await api.getHistory(); this.records = d.records; this.total = d.total; } catch(e) { console.error(e); } },
    async exportExcel() { try { await api.exportExcel(); } catch(e) { alert('导出失败: ' + e.message); } },
  },
};
</script>

<style scoped>
.history-root { max-width: 960px; margin: 0 auto; }
.glass-card {
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.06);
  color: #333;
}
.hist-header-bar { display: flex; align-items: center; justify-content: space-between; }
.hist-title { color: #333; font-size: 18px; display: flex; align-items: center; }
.hist-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 12px; }
.hist-card { display: flex; flex-direction: column; }
.hist-thumb { width: 100%; height: 120px; object-fit: cover; border-radius: 10px; margin-bottom: 10px; }
.hist-disease { color: #333; font-weight: 600; font-size: 14px; }
.hist-date { color: rgba(0,0,0,0.35); font-size: 11px; margin: 4px 0; }
.hist-chips { margin-top: 6px; }
.hist-empty { text-align: center; color: rgba(0,0,0,0.5); padding: 40px; }
.hist-empty-sub { font-size: 13px; margin-top: 4px; }

@media (max-width: 600px) {
  .hist-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
