
<template>
    <div class = "page">

        <h1>Cadastro</h1>

        <cadastroForm/>
        
    </div>



</template>

<script setup lang="ts">

import cadastroForm from '@/components/cadastroForm.vue'

</script>

<style scoped>

    .page {
        min-height: 100vh;
        background-color: var(--color-bg-base);
        padding: var(--padding-section) var(--padding-page-x);
    }

</style>