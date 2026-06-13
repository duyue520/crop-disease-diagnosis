<template>
  <div class="auth-glass-card">
    <!-- Tab 切换 -->
    <div class="auth-tabs">
      <button :class="['auth-tab', { active: !isRegister }]" @click="isRegister = false; error = ''">
        <v-icon size="18">mdi-login</v-icon> 登录
      </button>
      <button :class="['auth-tab', { active: isRegister }]" @click="isRegister = true; error = ''">
        <v-icon size="18">mdi-account-plus</v-icon> 注册
      </button>
    </div>

    <form @submit.prevent="handleSubmit" class="auth-form">
      <!-- 头像装饰 -->
      <div class="auth-avatar">
        <v-avatar size="72" color="green">
          <v-icon size="40" color="white">mdi-leaf</v-icon>
        </v-avatar>
      </div>

      <v-text-field
        v-model="username"
        label="用户名"
        variant="outlined"
        prepend-inner-icon="mdi-account-outline"
        density="comfortable"
        class="light-input"
        hide-details="auto"
        :rules="[v => !!v || '请输入用户名']"
        color="green-darken-2"
        base-color="grey-darken-2"
      />

      <v-text-field
        v-if="isRegister"
        v-model="email"
        label="邮箱"
        variant="outlined"
        prepend-inner-icon="mdi-email-outline"
        density="comfortable"
        class="light-input"
        hide-details="auto"
        :rules="[v => !!v || '请输入邮箱', v => v.includes('@') || '邮箱格式不正确']"
        color="green-darken-2"
        base-color="grey-darken-2"
      />

      <v-text-field
        v-model="password"
        label="密码"
        variant="outlined"
        prepend-inner-icon="mdi-lock-outline"
        density="comfortable"
        class="light-input"
        :type="showPwd ? 'text' : 'password'"
        :append-inner-icon="showPwd ? 'mdi-eye-off' : 'mdi-eye'"
        @click:append-inner="showPwd = !showPwd"
        hide-details="auto"
        :rules="[v => (v && v.length >= 6) || '密码至少6位']"
        color="green-darken-2"
        base-color="grey-darken-2"
      />

      <v-alert v-if="error" type="error" variant="tonal" density="compact" class="mt-2" closable @click:close="error = ''">
        {{ error }}
      </v-alert>

      <v-btn
        block
        size="x-large"
        type="submit"
        :loading="loading"
        variant="flat"
        color="green-darken-2"
        class="auth-submit-btn mt-4"
        rounded="lg"
      >
        <v-icon start>{{ isRegister ? 'mdi-account-plus' : 'mdi-login' }}</v-icon>
        {{ isRegister ? '创建账号' : '立即登录' }}
      </v-btn>

      <p class="auth-hint">
        {{ isRegister ? '已有账号？' : '没有账号？' }}
        <a @click.prevent="isRegister = !isRegister; error = ''">
          {{ isRegister ? '去登录' : '免费注册' }}
        </a>
      </p>

      <!-- 忘记密码 -->
      <p v-if="!isRegister" class="auth-hint mt-1">
        <a @click.prevent="showForgotPwd = !showForgotPwd" class="forgot-link">忘记密码？</a>
      </p>

      <v-expand-transition>
        <div v-if="showForgotPwd" class="forgot-section">
          <v-divider class="mb-3" />
          <p class="forgot-title">🔑 找回密码</p>
          <v-text-field v-model="fpUsername" label="用户名" variant="outlined" density="compact" hide-details class="light-input mb-2" color="green-darken-2" />
          <v-text-field v-model="fpEmail" label="注册邮箱" variant="outlined" density="compact" hide-details class="light-input mb-2" color="green-darken-2" />
          <v-text-field v-model="fpNewPwd" label="新密码 (至少6位)" variant="outlined" density="compact" :type="showFp ? 'text' : 'password'" :append-inner-icon="showFp ? 'mdi-eye-off' : 'mdi-eye'" @click:append-inner="showFp = !showFp" hide-details class="light-input mb-2" color="green-darken-2" />
          <v-btn block size="small" color="orange-darken-2" variant="flat" rounded="lg" :loading="fpLoading" @click="doResetPassword">
            <v-icon start size="16">mdi-lock-reset</v-icon> 重置密码
          </v-btn>
          <v-alert v-if="fpMsg" :type="fpErr ? 'error' : 'success'" density="compact" class="mt-2" closable @click:close="fpMsg = ''">
            {{ fpMsg }}
          </v-alert>
        </div>
      </v-expand-transition>
    </form>
  </div>
</template>

<script>
import api from '../../services/api.js';

export default {
  name: 'AuthCard',
  emits: ['login-success'],
  data() {
    return {
      isRegister: false,
      username: '',
      email: '',
      password: '',
      showPwd: false,
      loading: false,
      error: '',
      // 找回密码
      showForgotPwd: false,
      fpUsername: '', fpEmail: '', fpNewPwd: '', showFp: false,
      fpLoading: false, fpMsg: '', fpErr: false,
    };
  },
  methods: {
    async handleSubmit() {
      this.loading = true;
      this.error = '';
      try {
        if (this.isRegister) {
          await api.register(this.username, this.email, this.password);
        } else {
          await api.login(this.username, this.password);
        }
        this.$emit('login-success', api.getUser());
      } catch (e) {
        this.error = e.message;
      } finally {
        this.loading = false;
      }
    },
    async doResetPassword() {
      if (!this.fpUsername || !this.fpEmail || this.fpNewPwd.length < 6) {
        this.fpMsg = '请完整填写所有字段，新密码至少6位'; this.fpErr = true; return;
      }
      this.fpLoading = true; this.fpErr = false;
      try {
        const res = await api.resetPassword(this.fpUsername, this.fpEmail, this.fpNewPwd);
        this.fpMsg = res.message;
        this.showForgotPwd = false;
        // 自动填充登录表单
        this.username = this.fpUsername;
        this.password = this.fpNewPwd;
      } catch (e) {
        this.fpMsg = e.message; this.fpErr = true;
      } finally { this.fpLoading = false; }
    },
  },
};
</script>

<style scoped>
.auth-glass-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 20px;
  padding: 32px 28px 24px;
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.12);
}

.auth-tabs {
  display: flex;
  gap: 0;
  margin-bottom: 24px;
  background: rgba(0, 0, 0, 0.04);
  border-radius: 12px;
  padding: 4px;
}
.auth-tab {
  flex: 1;
  padding: 10px 16px;
  border: none;
  border-radius: 10px;
  background: transparent;
  color: rgba(0, 0, 0, 0.5);
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}
.auth-tab.active {
  background: white;
  color: #2e7d32;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.auth-avatar {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.light-input :deep(.v-field) {
  border-radius: 12px !important;
  background: rgba(255, 255, 255, 0.7) !important;
}
.light-input :deep(.v-field__outline) {
  --v-field-border-opacity: 0.25;
}
.light-input :deep(.v-label) {
  color: rgba(0, 0, 0, 0.55);
}
.light-input :deep(input) {
  color: #333;
}

.auth-submit-btn {
  height: 52px !important;
  font-size: 16px !important;
  font-weight: 600 !important;
  letter-spacing: 1px;
  box-shadow: 0 4px 16px rgba(46, 125, 50, 0.3) !important;
}

.auth-hint {
  text-align: center;
  color: rgba(0, 0, 0, 0.45);
  font-size: 13px;
  margin-top: 4px;
}
.auth-hint a {
  color: #2e7d32;
  cursor: pointer;
  font-weight: 600;
}
.forgot-link { color: #e65100 !important; font-size: 12px; }
.forgot-section { padding-top: 8px; }
.forgot-title { font-size: 14px; color: #333; font-weight: 600; margin-bottom: 8px; }
</style>
