

<template>
    <div class = "page">

        <LoginForm/>

        <!-- <p>teste</p> -->

    </div>

</template>

<script setup lang="ts">

import LoginForm from '@/components/loginForm.vue';

</script>

<style scoped>

    :global(html),
    :global(body),
    :global(#app) {
        margin: 0;
        padding: 0; 
        box-sizing: border-box;
        
    }

    .page{
        background-color: #061c42;
    }


</style>
