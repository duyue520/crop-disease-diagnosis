<template>
  <div class="profile-root">
    <div class="glass-card">
      <!-- 头像区 -->
      <div class="avatar-section">
        <div class="avatar-preview" @click="showAvatarMenu = !showAvatarMenu">
          <img v-if="avatarPreview" :src="avatarPreview" class="avatar-img" />
          <v-icon v-else size="80" color="grey-lighten-1">mdi-account-circle</v-icon>
          <div class="avatar-overlay">
            <v-icon size="24" color="white">mdi-camera</v-icon>
          </div>
        </div>
        <p class="avatar-hint">点击头像更换</p>

        <!-- 头像选择菜单 -->
        <v-expand-transition>
          <div v-if="showAvatarMenu" class="avatar-menu">
            <input ref="cameraInput" type="file" accept="image/*" capture="environment" style="display:none" @change="onCameraCapture" />
            <input ref="galleryInput" type="file" accept="image/*" style="display:none" @change="onGalleryPick" />

            <v-btn block variant="tonal" color="green-darken-2" rounded="lg" size="small" class="mb-2" @click="$refs.cameraInput.click()">
              <v-icon start size="18">mdi-camera</v-icon> 拍照
            </v-btn>
            <v-btn block variant="tonal" color="blue-darken-2" rounded="lg" size="small" class="mb-2" @click="$refs.galleryInput.click()">
              <v-icon start size="18">mdi-image</v-icon> 相册选择
            </v-btn>
            <v-btn block variant="tonal" color="orange-darken-2" rounded="lg" size="small" @click="randomAvatar">
              <v-icon start size="18">mdi-dice-5</v-icon> 随机生成
            </v-btn>
          </div>
        </v-expand-transition>
      </div>

      <!-- 用户名 -->
      <div class="profile-field">
        <label>用户名</label>
        <v-text-field
          v-model="editUsername"
          variant="outlined"
          density="compact"
          hide-details
          class="light-input"
          color="green-darken-2"
          bg-color="rgba(255,255,255,0.7)"
        />
      </div>

      <!-- 邮箱（只读） -->
      <div class="profile-field">
        <label>邮箱</label>
        <v-text-field
          v-model="email"
          variant="outlined"
          density="compact"
          readonly
          hide-details
          class="light-input"
          bg-color="rgba(0,0,0,0.04)"
        />
      </div>

      <v-btn block color="green-darken-2" variant="flat" rounded="lg" size="large" class="mt-3" :loading="saving" @click="saveProfile">
        <v-icon start>mdi-content-save</v-icon> 保存资料
      </v-btn>

      <v-alert v-if="saveMsg" :type="saveErr ? 'error' : 'success'" density="compact" class="mt-2" closable @click:close="saveMsg = ''">
        {{ saveMsg }}
      </v-alert>
    </div>

    <!-- 修改密码 -->
    <div class="glass-card mt-3">
      <h3 class="section-title"><v-icon start color="orange">mdi-lock-reset</v-icon> 修改密码</h3>
      <v-text-field v-model="oldPwd" label="原密码" variant="outlined" density="compact" :type="showOld ? 'text' : 'password'" :append-inner-icon="showOld ? 'mdi-eye-off' : 'mdi-eye'" @click:append-inner="showOld = !showOld" hide-details class="light-input mb-2" bg-color="rgba(255,255,255,0.7)" />
      <v-text-field v-model="newPwd" label="新密码 (至少6位)" variant="outlined" density="compact" :type="showNew ? 'text' : 'password'" :append-inner-icon="showNew ? 'mdi-eye-off' : 'mdi-eye'" @click:append-inner="showNew = !showNew" hide-details class="light-input mb-2" bg-color="rgba(255,255,255,0.7)" />
      <v-btn block color="orange-darken-2" variant="flat" rounded="lg" size="large" :loading="changingPwd" @click="changePwd">
        <v-icon start>mdi-shield-check</v-icon> 修改密码
      </v-btn>
      <v-alert v-if="pwdMsg" :type="pwdErr ? 'error' : 'success'" density="compact" class="mt-2" closable @click:close="pwdMsg = ''">
        {{ pwdMsg }}
      </v-alert>
    </div>
  </div>
</template>

<script>
import api from '../../services/api.js';

export default {
  name: 'UserProfile',
  emits: ['updated'],
  data() {
    return {
      editUsername: '',
      email: '',
      avatarPreview: '',
      avatarBase64: '',
      showAvatarMenu: false,
      saving: false, saveMsg: '', saveErr: false,
      oldPwd: '', newPwd: '', showOld: false, showNew: false,
      changingPwd: false, pwdMsg: '', pwdErr: false,
    };
  },
  mounted() { this.loadProfile(); },
  methods: {
    async loadProfile() {
      try {
        const p = await api.getProfile();
        this.editUsername = p.username;
        this.email = p.email;
        if (p.avatar_base64) {
          this.avatarBase64 = p.avatar_base64;
          this.avatarPreview = `data:image/jpeg;base64,${p.avatar_base64}`;
        }
      } catch (e) { console.error(e); }
    },
    async onCameraCapture(e) {
      const f = e.target.files?.[0];
      if (f) await this.uploadAvatarFile(f);
    },
    async onGalleryPick(e) {
      const f = e.target.files?.[0];
      if (f) await this.uploadAvatarFile(f);
    },
    async uploadAvatarFile(file) {
      try {
        const res = await api.uploadAvatar(file);
        this.avatarBase64 = res.avatar_base64;
        this.avatarPreview = `data:image/jpeg;base64,${res.avatar_base64}`;
        this.showAvatarMenu = false;
      } catch (e) { alert('上传失败: ' + e.message); }
    },
    randomAvatar() {
      // 随机生成一个彩色 SVG 头像
      const colors = ['#2e7d32','#1565c0','#c62828','#e65100','#6a1b9a','#00838f','#283593','#ad1457'];
      const color = colors[Math.floor(Math.random() * colors.length)];
      const init = (this.editUsername || 'U')[0].toUpperCase();
      const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">
        <rect width="200" height="200" fill="${color}"/>
        <text x="100" y="135" font-family="Arial" font-size="100" font-weight="bold" fill="white" text-anchor="middle">${init}</text>
      </svg>`;
      this.avatarBase64 = btoa(svg);
      this.avatarPreview = `data:image/svg+xml;base64,${this.avatarBase64}`;
      this.showAvatarMenu = false;
    },
    async saveProfile() {
      this.saving = true; this.saveErr = false;
      try {
        const res = await api.updateProfile(this.editUsername, this.avatarBase64);
        this.saveMsg = res.message;
        this.$emit('updated', { username: res.username, avatar: this.avatarPreview });
      } catch (e) { this.saveMsg = e.message; this.saveErr = true; }
      finally { this.saving = false; }
    },
    async changePwd() {
      if (!this.oldPwd || this.newPwd.length < 6) { this.pwdMsg = '请填写完整，新密码至少6位'; this.pwdErr = true; return; }
      this.changingPwd = true; this.pwdErr = false;
      try {
        const res = await api.changePassword(this.oldPwd, this.newPwd);
        this.pwdMsg = res.message;
        this.oldPwd = ''; this.newPwd = '';
      } catch (e) { this.pwdMsg = e.message; this.pwdErr = true; }
      finally { this.changingPwd = false; }
    },
  },
};
</script>

<style scoped>
.profile-root { max-width: 600px; margin: 0 auto; }
.glass-card {
  background: rgba(255, 255, 255, 0.78);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255,255,255,0.5);
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.06);
  color: #333;
}
.avatar-section { text-align: center; margin-bottom: 20px; }
.avatar-preview {
  width: 96px; height: 96px; border-radius: 50%; margin: 0 auto;
  background: rgba(0,0,0,0.05); display: flex; align-items: center; justify-content: center;
  cursor: pointer; position: relative; overflow: hidden;
}
.avatar-img { width: 100%; height: 100%; object-fit: cover; }
.avatar-overlay {
  position: absolute; inset: 0; background: rgba(0,0,0,0.3);
  display: flex; align-items: center; justify-content: center;
  opacity: 0; transition: opacity 0.3s;
}
.avatar-preview:hover .avatar-overlay { opacity: 1; }
.avatar-hint { font-size: 13px; color: rgba(0,0,0,0.4); margin-top: 6px; }
.avatar-menu { max-width: 260px; margin: 12px auto 0; }
.profile-field { margin-bottom: 12px; }
.profile-field label { font-size: 13px; color: rgba(0,0,0,0.5); margin-bottom: 4px; display: block; }
.light-input :deep(.v-field) { border-radius: 10px !important; }
.light-input :deep(input) { color: #333 !important; }
.section-title { font-size: 17px; margin-bottom: 14px; display: flex; align-items: center; color: #333; }
</style>
