
<template>
    <div class = "page">

        <h1>Cadastro</h1>

        <cadastroForm/>
        
    </div>



</template>

<script setup lang="js">

import { RouterView } from 'vue-router'
import cadastroForm from '@/components/cadastroForm.vue'

</script>

<style scoped>

    :global(html),
    :global(body),
    :global(#app) {
        margin: 0;
        padding: 0; 
        box-sizing: border-box;
        background-color: #dfdfdf;
    }

</style>