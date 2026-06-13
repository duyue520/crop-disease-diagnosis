<template>
  <v-dialog v-model="visible" width="500" :scrim="true" transition="dialog-bottom-transition">
    <v-card class="profile-dialog-glass" rounded="xl">
      <v-toolbar color="transparent" density="compact" flat>
        <v-toolbar-title class="text-body-1 font-weight-bold">
          <v-icon start color="green-darken-2">mdi-account-cog</v-icon> 个人中心
        </v-toolbar-title>
        <v-spacer />
        <v-btn icon size="small" variant="text" @click="visible = false">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-toolbar>
      <v-card-text class="pt-0">
        <UserProfile @updated="onUpdated" />
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
import UserProfile from './disease/UserProfile.vue';
import api from '../services/api.js';

export default {
  name: 'ProfileDialog',
  components: { UserProfile },
  emits: ['updated'],
  data() {
    return { visible: false };
  },
  methods: {
    open() {
      this.visible = true;
    },
    onUpdated(data) {
      this.$emit('updated', data);
    },
  },
};
</script>

<style scoped>
.profile-dialog-glass {
  background: rgba(255, 255, 255, 0.92) !important;
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(255,255,255,0.5);
}
</style>
