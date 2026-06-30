<template>

    <baseCard>
    
        <h1>ERRO</h1>
        <h1>403</h1>
        <p>Você não tem permissão para acessar essa área.</p>
        <button @click="goHome">Voltar para Home</button>
    
    </baseCard>

</template>

<script setup lang="ts">

import baseCard from './baseCard.vue';
import { useRouter } from 'vue-router';

const router = useRouter()

function goHome() {
    router.push('/')
}

</script>

<style scoped>

    h1 {
        color: #facc15;
        font-size: 56px;
        margin: 0;
    }

    p {
        color: white;
        text-align: center;
        margin-top: 30px;
    }

    button {
        margin-top: 40px;
        width: 100%;
        padding: 16px;
        border: none;
        border-radius: 15px;
        background: #eab308;
        font-weight: bold;
        cursor: pointer;   
        font-size: 18px;
    }
</style>