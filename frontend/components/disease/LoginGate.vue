<template>
  <transition name="fade">
    <div v-if="show" class="login-gate-overlay">
      <div class="login-gate-bg"></div>
      <div class="login-gate-content">
        <div class="gate-header">
          <v-avatar size="80" class="gate-avatar mb-3">
            <v-img :src="avatar" cover />
          </v-avatar>
          <h2 class="gate-title">欢迎来到 越 的世界</h2>
          <p class="gate-sub">登录一次，七天内自动进入</p>
        </div>

        <auth-card @login-success="onLoginSuccess" />


      </div>
    </div>
  </transition>
</template>

<script>
import api from '../../services/api.js';
import AuthCard from './AuthCard.vue';

export default {
  name: 'LoginGate',
  components: { AuthCard },
  props: { avatar: { type: String, default: '/img/avatar.jpg' } },
  emits: ['done'],
  data() {
    return { show: true };
  },
  methods: {
    onLoginSuccess() {
      this.show = false;
      this.$emit('done', { loggedIn: true, user: api.getUser() });
    },
  },
};
</script>

<style scoped>
.login-gate-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}
.login-gate-bg {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.55);
  backdrop-filter: blur(28px);
  -webkit-backdrop-filter: blur(28px);
}
.login-gate-content {
  position: relative;
  width: 100%;
  max-width: 420px;
  padding: 0 20px;
  z-index: 1;
  max-height: 90vh;
  overflow-y: auto;
}
.gate-header { text-align: center; margin-bottom: 20px; }
.gate-avatar { border: 3px solid rgba(46, 125, 50, 0.3); }
.gate-title { font-size: 22px; font-weight: 700; color: #2e7d32; margin: 0; }
.gate-sub { color: rgba(0, 0, 0, 0.5); font-size: 14px; margin-top: 6px; }
.gate-actions { text-align: center; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.4s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

@media (max-width: 600px) {
  .login-gate-content { padding: 0 12px; max-height: 95vh; }
  .gate-title { font-size: 18px; }
}
</style>
