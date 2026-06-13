<template>
  <div class="diag-root">
    <!-- 上传区 -->
    <div v-if="!result && !loading" class="glass-card upload-card">
      <input ref="fileInput" type="file" accept="image/*" capture="environment" style="display:none" @change="onFileSelected" />

      <div class="upload-drag-zone" @click="$refs.fileInput.click()" @drop.prevent="onDrop" @dragover.prevent>
        <v-icon size="72" color="green-accent-3">mdi-image-plus</v-icon>
        <p class="upload-title">点击或拖拽上传叶片照片</p>
        <p class="upload-sub">支持 JPG / PNG / WebP · 最大 10MB</p>
      </div>

      <!-- 手机拍照 -->
      <div v-if="isMobile" class="mobile-capture">
        <div class="capture-divider"><span>手机端选择</span></div>
        <v-btn block size="x-large" color="green-darken-2" variant="flat" rounded="lg" class="mb-3" @click="capturePhoto">
          <v-icon start size="24">mdi-camera</v-icon> 📸 拍摄叶片照片
        </v-btn>
      </div>
      <div v-else class="mobile-capture">
        <div class="capture-divider"><span>电脑端选择</span></div>
      </div>

      <v-btn block size="large" variant="tonal" color="green-accent-3" rounded="lg" @click="$refs.fileInput.click()">
        <v-icon start>mdi-folder-image</v-icon> 从相册选择图片
      </v-btn>

      <v-switch v-model="enableGradcam" color="green-accent-3" label="生成热力图显示关注区域" density="compact" hide-details class="mt-3 text-grey-lighten-2" />
    </div>

    <!-- Loading -->
    <div v-if="loading" class="glass-card loading-card">
      <v-progress-circular indeterminate color="green-accent-3" size="72" width="5" />
      <p class="loading-text mt-4">AI 正在分析叶片...</p>
      <p class="loading-sub">约需 1 ~ 3 秒</p>
    </div>

    <!-- 结果 -->
    <div v-if="result && !loading" class="result-area">
      <!-- 图片 + 结论 -->
      <div class="glass-card result-top">
        <div class="result-preview" :class="{ 'result-preview-mobile': isMobile }">
          <img v-if="!result.grad_cam_base64" :src="previewUrl" class="preview-img" />
          <img v-else :src="'data:image/jpeg;base64,' + result.grad_cam_base64" class="preview-img" />
          <div class="preview-badges">
            <v-chip :color="result.is_healthy ? 'green' : 'red-darken-2'" size="small" pill>
              <v-icon start size="16">{{ result.is_healthy ? 'mdi-check-circle' : 'mdi-alert-circle' }}</v-icon>
              {{ result.is_healthy ? '健康' : '病害' }}
            </v-chip>
            <v-chip v-if="!result.is_healthy" size="small" pill :color="severityColor" class="ml-1">
              {{ severityLabel }} {{ result.severity_percent }}%
            </v-chip>
          </div>
        </div>

        <div class="result-predictions">
          <h3 class="result-title">🎯 诊断结果</h3>
          <div v-for="p in result.predictions" :key="p.rank" class="pred-item" :class="{ 'pred-top': p.rank === 1 }">
            <div class="pred-header">
              <span class="pred-rank">{{ ['🥇','🥈','🥉'][p.rank-1] }}</span>
              <span class="pred-name">{{ p.disease_cn }}</span>
              <span class="pred-conf">{{ p.confidence }}%</span>
            </div>
            <v-progress-linear :model-value="p.confidence" :color="p.rank === 1 ? 'green-accent-3' : p.rank === 2 ? 'orange' : 'grey'" height="6" rounded class="pred-bar" />
          </div>
          <p class="inference-info">⚡ 推理耗时 {{ result.inference_time_ms }}ms · ResNet18 · 39类 · 99.4%准确率</p>
        </div>
      </div>

      <!-- 防治建议 -->
      <div v-if="result.advices" class="glass-card advice-card">
        <h4><v-icon color="orange" start>mdi-flask-round-bottom</v-icon> 防治建议</h4>
        <div class="advice-item"><strong>🛡️ 推荐农药：</strong>{{ result.advices.pesticide }}</div>
        <div class="advice-item"><strong>🌱 农艺措施：</strong>{{ result.advices.method }}</div>
      </div>

      <!-- 操作 -->
      <div class="action-row">
        <v-btn variant="tonal" color="green-accent-3" rounded="lg" prepend-icon="mdi-refresh" @click="reset">重新诊断</v-btn>
        <v-btn variant="tonal" color="blue-lighten-2" rounded="lg" prepend-icon="mdi-content-copy" @click="copyResult">复制结果</v-btn>
        <v-btn v-if="result.diagnosis_id" variant="tonal" color="orange-lighten-1" rounded="lg" prepend-icon="mdi-pencil" @click="showCorrection = !showCorrection">纠错</v-btn>
      </div>

      <!-- 纠错 -->
      <div v-if="showCorrection" class="glass-card correction-card">
        <p class="text-body-2 mb-2">请选择正确的病害标签：</p>
        <v-select v-model="correctedLabel" :items="diseaseOptions" label="正确病害" variant="outlined" density="compact" class="mb-2" bg-color="rgba(255,255,255,0.06)" />
        <v-btn block color="orange" rounded="lg" variant="flat" @click="submitCorrection" :loading="correcting">提交纠错，帮助我们改进模型</v-btn>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../../services/api.js';

export default {
  name: 'DiagnosisTab',
  data() {
    return {
      loading: false,
      result: null,
      previewUrl: '',
      enableGradcam: false,
      showCorrection: false,
      correctedLabel: null,
      correcting: false,
      isMobile: /Android|iPhone|iPad|iPod/i.test(navigator.userAgent),
    };
  },
  computed: {
    severityColor() {
      return { mild: 'green', moderate: 'orange', severe: 'red' }[this.result?.severity] || 'grey';
    },
    severityLabel() {
      return { mild: '轻度', moderate: '中度', severe: '重度' }[this.result?.severity] || '';
    },
    diseaseOptions() {
      return (this.result?.predictions || []).map(p => ({ title: p.disease_cn, value: p.disease_cn }));
    },
  },
  methods: {
    capturePhoto() {
      const input = this.$refs.fileInput;
      input.setAttribute('capture', 'environment');
      input.click();
    },
    onFileSelected(e) { const f = e.target.files?.[0]; if (f) this.processFile(f); },
    onDrop(e) { const f = e.dataTransfer?.files?.[0]; if (f) this.processFile(f); },
    async processFile(file) {
      if (file.size > 10 * 1024 * 1024) { alert('图片不能超过 10MB'); return; }
      this.previewUrl = URL.createObjectURL(file);
      this.result = null;
      this.loading = true;
      try { this.result = await api.predict(file, this.enableGradcam); }
      catch (e) { alert('诊断失败: ' + e.message); }
      finally { this.loading = false; }
    },
    reset() { this.result = null; this.previewUrl = ''; this.showCorrection = false; this.correctedLabel = null; },
    async copyResult() {
      const t = this.result.predictions.map(p => `${p.rank === 1 ? '确诊' : '备选' + p.rank}: ${p.disease_cn} (${p.confidence}%)`).join('\n');
      await navigator.clipboard.writeText(t);
      alert('已复制诊断结果！');
    },
    async submitCorrection() {
      if (!this.correctedLabel) return;
      this.correcting = true;
      try { await api.correctPrediction(this.result.diagnosis_id, this.result.predictions[0].disease_cn, this.correctedLabel); alert('纠错已提交，感谢！'); this.showCorrection = false; }
      catch (e) { alert('提交失败: ' + e.message); }
      finally { this.correcting = false; }
    },
  },
};
</script>

<style scoped>
.diag-root { max-width: 800px; margin: 0 auto; }

/* 毛玻璃卡片 */
.glass-card {
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 20px;
  padding: 28px;
  margin-bottom: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.06);
  color: #333;
}

/* 上传区 */
.upload-drag-zone {
  border: 2px dashed rgba(0, 0, 0, 0.15);
  border-radius: 16px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}
.upload-drag-zone:hover {
  border-color: #4caf50;
  background: rgba(76, 175, 80, 0.06);
}
.upload-title { color: #333; font-size: 18px; font-weight: 500; margin: 12px 0 4px; }
.upload-sub { color: rgba(0,0,0,0.45); font-size: 13px; }

.capture-divider { text-align: center; margin: 16px 0 12px; }
.capture-divider span { color: rgba(0,0,0,0.4); font-size: 13px; padding: 0 12px; }

/* Loading */
.loading-card { text-align: center; padding: 60px 20px; }
.loading-text { color: #333; font-size: 20px; font-weight: 500; }
.loading-sub { color: rgba(0,0,0,0.4); font-size: 14px; }

/* 结果 */
.result-preview { text-align: center; margin-bottom: 16px; }
.result-preview-mobile { max-width: 280px; margin: 0 auto 16px; }
.preview-img { width: 100%; max-height: 280px; object-fit: cover; border-radius: 12px; }
.preview-badges { margin-top: 10px; display: flex; justify-content: center; gap: 6px; }

.result-title { color: #333; font-size: 20px; margin-bottom: 12px; }
.pred-item {
  background: rgba(0,0,0,0.03);
  border-radius: 12px;
  padding: 12px 16px;
  margin-bottom: 8px;
}
.pred-top { background: rgba(76, 175, 80, 0.12); border: 1px solid rgba(76, 175, 80, 0.2); }
.pred-header { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.pred-rank { font-size: 18px; }
.pred-name { flex: 1; color: #333; font-size: 15px; font-weight: 500; }
.pred-conf { color: #4caf50; font-weight: 700; font-size: 15px; }
.pred-bar { margin: 0; }
.inference-info { color: rgba(0,0,0,0.4); font-size: 12px; text-align: center; margin-top: 8px; }

/* 防治 */
.advice-card h4 { color: #333; font-size: 16px; margin-bottom: 10px; display: flex; align-items: center; }
.advice-item { color: rgba(0,0,0,0.7); font-size: 14px; line-height: 1.8; }

/* 操作 */
.action-row { display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; margin-bottom: 16px; }

.correction-card { margin-top: 8px; }
</style>
