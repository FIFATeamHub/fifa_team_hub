

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

    } catch (error) {
    if (error.status === 401) {
      errorMessage.value = 'E-mail ou senha incorretos'
    } else {
      errorMessage.value = 'Ocorreu um erro no servidor. Verifique os dados e tente novamente.'
    }
    console.error(error) // Isso imprime o erro no F12 para você debugar!
  }

}
</script>
    .page{
        background-color: #061c42;
    }


</style>
