<!-- <template>
  <header>
    <nav>
      <RouterLink to="/">Home</RouterLink>
      <RouterLink to="/times">Times</RouterLink>
      <RouterLink to="/login">LoginPage</RouterLink>
      <RouterLink to="/dashboard">DashboardPage</RouterLink>  # TESTANDO
      <RouterLink to="/upload">UploadPage</RouterLink>
      <RouterLink to="/audit">AuditPage</RouterLink>  
    </nav>
  </header>

  <main>
    <RouterView />
  </main>
</template> -->



<template>
  <Navbar v-if="!['login', 'cadastro'].includes(String(route.name))" />

  <main>
    <RouterView />
  </main>
</template>

<script setup lang="ts">

import { useRoute } from 'vue-router'
import Navbar from '@/components/navbar.vue'

const route = useRoute()

</script>

<style scoped></style>
