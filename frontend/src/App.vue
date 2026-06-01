<script setup lang="js">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <header>
    <nav>
      <RouterLink to="/">Home</RouterLink>
      <RouterLink to="/times">Times</RouterLink>
      <RouterLink to="/login">LoginPage</RouterLink>
      <RouterLink to="/dashboard">DashboardPage</RouterLink>
      <RouterLink to="/upload">UploadPage</RouterLink>
      <RouterLink to="/audit">AuditPage</RouterLink>  
    </nav>
  </header>

  <main>
    <RouterView />
  </main>
</template>

<style scoped></style>