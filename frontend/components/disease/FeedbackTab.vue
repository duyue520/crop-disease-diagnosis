<template>
  <div class="fb-root">
    <!-- 提交反馈 -->
    <div class="glass-card">
      <h3 class="fb-title"><v-icon color="green-accent-3" start size="24">mdi-message-plus</v-icon> 提交反馈</h3>

      <div class="fb-cats">
        <button v-for="c in categories" :key="c.value" :class="['fb-cat-btn', { active: category === c.value }]" @click="category = c.value">
          <v-icon size="16">{{ c.icon }}</v-icon> {{ c.title }}
        </button>
      </div>

      <v-text-field v-model="title" label="标题" variant="outlined" density="comfortable" class="glass-input mt-3" hide-details="auto" :rules="[v => !!v || '请输入标题']" bg-color="rgba(255,255,255,0.06)" color="green-accent-3" />

      <v-textarea v-model="content" label="详细描述" variant="outlined" rows="4" density="comfortable" class="glass-input mt-3" hide-details="auto" :rules="[v => !!v || '请输入内容']" bg-color="rgba(255,255,255,0.06)" color="green-accent-3" />

      <v-btn block size="large" color="green-darken-2" variant="flat" rounded="lg" class="mt-3 fb-submit" :loading="submitting" @click="submitFeedback">
        <v-icon start>mdi-send</v-icon> 提交反馈
      </v-btn>

      <v-alert v-if="submitOK" type="success" variant="tonal" density="compact" class="mt-3" closable @click:close="submitOK = false">谢谢你的反馈，我会继续努力！</v-alert>
    </div>

    <!-- 反馈列表 -->
    <div v-if="feedbacks.length > 0" :key="listKey" class="glass-card">
      <h3 class="fb-title"><v-icon color="green-accent-3" start size="24">mdi-message-text</v-icon> 我的反馈 ({{ feedbacks.length }})</h3>

      <div v-for="fb in feedbacks" :key="fb.id" class="fb-item">
        <div class="fb-item-header">
          <v-chip size="x-small" :color="catColor(fb.category)" pill>{{ catLabel(fb.category) }}</v-chip>
          <span class="fb-item-title">{{ fb.title }}</span>
          <span class="fb-item-date">{{ fb.created_at?.slice(0, 10) }}</span>
        </div>
        <p class="fb-item-content">{{ fb.content }}</p>
        <div v-if="fb.reply" class="fb-reply">
          <strong>🧑‍🌾 管理员回复：</strong>{{ fb.reply }}
        </div>
        <div v-else class="fb-reply fb-reply-pending">⏳ 等待回复中...</div>
      </div>
    </div>

    <div v-else class="glass-card fb-empty">
      <v-icon size="48" color="grey-lighten-1">mdi-message-outline</v-icon>
      <p>暂无反馈记录</p>
      <p class="fb-empty-sub">提交你的第一条建议或 Bug 报告吧</p>
    </div>
  </div>
</template>

<script>
import api from '../../services/api.js';

export default {
  name: 'FeedbackTab',
  data() {
    return {
      category: 'suggestion', title: '', content: '',
      submitting: false, submitOK: false, feedbacks: [], listKey: 0,
      categories: [
        { title: '功能建议', value: 'suggestion', icon: 'mdi-lightbulb-on' },
        { title: 'Bug 报告', value: 'bug', icon: 'mdi-bug' },
        { title: '使用问题', value: 'question', icon: 'mdi-help-circle' },
        { title: '其他', value: 'other', icon: 'mdi-dots-horizontal' },
      ],
    };
  },
  mounted() { this.loadFeedbacks(); },
  methods: {
    async submitFeedback() {
      if (!this.title.trim() || !this.content.trim()) { alert('请填写标题和内容'); return; }
      this.submitting = true;
      try {
        await api.submitFeedback(this.category, this.title, this.content);
        this.submitOK = true; this.title = ''; this.content = '';
        await this.loadFeedbacks();
      } catch (e) { alert('提交失败: ' + e.message); }
      finally { this.submitting = false; }
    },
    async loadFeedbacks() {
      try { const d = await api.getMyFeedbacks(); this.feedbacks = d.items || []; this.listKey++; }
      catch (e) { console.error(e); }
    },
    catLabel(c) { return { bug: 'Bug', suggestion: '建议', question: '问题', other: '其他' }[c] || c; },
    catColor(c) { return { bug: 'red', suggestion: 'blue', question: 'orange', other: 'grey' }[c] || 'grey'; },
  },
};
</script>

<style scoped>
.fb-root { max-width: 800px; margin: 0 auto; }

.glass-card {
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.06);
  color: #333;
}

.fb-title { color: #333; font-size: 18px; margin-bottom: 16px; display: flex; align-items: center; }

.fb-cats { display: flex; gap: 8px; flex-wrap: wrap; }
.fb-cat-btn {
  background: rgba(0,0,0,0.04);
  border: 1px solid rgba(0,0,0,0.1);
  color: rgba(0,0,0,0.5);
  border-radius: 10px;
  padding: 8px 14px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 4px;
}
.fb-cat-btn.active {
  background: rgba(76,175,80,0.15);
  border-color: rgba(76,175,80,0.4);
  color: #2e7d32;
  font-weight: 600;
}

.glass-input { border-radius: 12px; }
.glass-input :deep(.v-field) { border-radius: 12px !important; background: rgba(255,255,255,0.7) !important; }
.glass-input :deep(input), .glass-input :deep(textarea) { color: #333 !important; }
.glass-input :deep(.v-label) { color: rgba(0,0,0,0.5) !important; }

.fb-submit { height: 48px; font-weight: 600; box-shadow: 0 4px 16px rgba(76,175,80,0.3); }

.fb-item {
  background: rgba(0,0,0,0.03);
  border-radius: 12px;
  padding: 14px 16px;
  margin-bottom: 10px;
}
.fb-item-header { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.fb-item-title { color: #333; font-weight: 500; flex: 1; }
.fb-item-date { color: rgba(0,0,0,0.35); font-size: 12px; }
.fb-item-content { color: rgba(0,0,0,0.6); font-size: 14px; line-height: 1.6; margin: 8px 0; }
.fb-reply { background: rgba(76,175,80,0.1); border-radius: 8px; padding: 10px 14px; color: rgba(0,0,0,0.7); font-size: 13px; margin-top: 8px; }
.fb-reply-pending { background: rgba(0,0,0,0.03); color: rgba(0,0,0,0.3); }
.fb-empty { text-align: center; color: rgba(0,0,0,0.5); padding: 40px; }
.fb-empty-sub { font-size: 13px; margin-top: 4px; }
</style>
