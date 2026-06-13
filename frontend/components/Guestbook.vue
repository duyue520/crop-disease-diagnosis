<template>
  <div class="gb-outer">
    <v-card class="gb-card" variant="tonal">
      <v-card-title class="pb-1">
        <span class="gb-title">💬 留言板</span>
        <v-spacer />
        <span class="gb-total">{{ messages.length }} 条留言</span>
      </v-card-title>
      <v-card-text class="pt-1">
        <!-- 输入 -->
        <div class="gb-send">
          <v-text-field
            v-model="newMsg"
            placeholder="留下你想说的话..."
            variant="outlined"
            density="compact"
            hide-details
            class="gb-input"
            bg-color="rgba(255,255,255,0.45)"
            @keyup.enter="postMessage"
          >
            <template #append-inner>
              <v-btn icon size="28" variant="flat" color="grey-darken-1" :loading="posting" @click="postMessage">
                <v-icon size="18">mdi-send</v-icon>
              </v-btn>
            </template>
          </v-text-field>
        </div>
        <!-- 列表 -->
        <div class="gb-list" v-if="messages.length > 0">
          <div v-for="m in messages" :key="m.id" class="gb-item">
            <span class="gb-nick">{{ m.nickname }}</span>
            <span class="gb-time">{{ m.created_at }}</span>
            <p class="gb-text">{{ m.content }}</p>
          </div>
        </div>
        <div v-else class="gb-empty">
          <p>还没有留言，来坐沙发吧 ~</p>
        </div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
import api from '../services/api.js';

export default {
  name: 'Guestbook',
  data() {
    return { newMsg: '', posting: false, messages: [] };
  },
  mounted() { this.loadMessages(); },
  methods: {
    async loadMessages() {
      try { const d = await api.getGuestbookMessages(); this.messages = d.messages || []; }
      catch (e) { console.error(e); }
    },
    async postMessage() {
      if (!this.newMsg.trim()) return;
      this.posting = true;
      try {
        const name = '匿名';
        await api.postGuestbookMessage(name, this.newMsg.trim());
        this.newMsg = '';
        await this.loadMessages();
      } catch (e) { alert('发送失败'); }
      finally { this.posting = false; }
    },
  },
};
</script>

<style scoped>
.gb-outer { margin: 18px 12px; max-width: 960px; }
.gb-card {
  background: rgba(255,255,255,0.4) !important;
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border: 1px solid rgba(255,255,255,0.25);
  border-radius: 16px !important;
  box-shadow: 0 2px 16px rgba(0,0,0,0.04);
}
.gb-title { font-weight: 700; font-size: 15px; color: #333; }
.gb-total { font-size: 12px; color: rgba(0,0,0,0.35); }
.gb-send { margin-bottom: 10px; }
.gb-input :deep(.v-field) { border-radius: 12px !important; box-shadow: 0 1px 4px rgba(0,0,0,0.04); }
.gb-input :deep(input) { color: #444 !important; font-size: 13px; }
.gb-list { max-height: 280px; overflow-y: auto; }
.gb-item { padding: 8px 12px; margin-bottom: 6px; background: rgba(255,255,255,0.35); border-radius: 10px; }
.gb-nick { font-weight: 600; font-size: 13px; color: #555; }
.gb-time { font-size: 11px; color: rgba(0,0,0,0.3); margin-left: 10px; }
.gb-text { color: #555; font-size: 13px; line-height: 1.5; margin: 4px 0 0; }
.gb-empty { text-align: center; padding: 20px; color: rgba(0,0,0,0.25); }
.gb-empty p { font-size: 13px; }

@media (max-width: 600px) {
  .gb-outer { margin: 12px 8px; }
}
</style>
