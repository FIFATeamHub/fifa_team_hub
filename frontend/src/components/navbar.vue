<template>
    <div class = "body">

    <div class = "container-nav">
        <RouterLink to = "/">
            <img class = "logo" src="/img/logo-copa-branca-removebg.png" alt = "Logo da copa do mundo de 2026">
        </RouterLink>

        <nav class = "container-pages">
            <RouterLink to="/">Home</RouterLink>
            <RouterLink to="/times">Times</RouterLink>
            <RouterLink to="/login">LoginPage</RouterLink>
            <RouterLink to="/dashboard">DashboardPage</RouterLink>
            <RouterLink to="/upload">UploadPage</RouterLink>
            <RouterLink to="/audit">AuditPage</RouterLink>  
        </nav>

    </div>

    </div>

</template>

<script lang="ts">

export default{
    name : "navbar"
}

</script>

<style scoped>

    :global(html),
    :global(body),
    :global(#app) {
        margin: 0;
        padding: 0;
        width: 100%;
    }

    img {
        width: 32px;
        height: 45px;
        padding: 11px;
        margin-left: 20px;

    }

    .container-nav {

        background-color: black;
        display: flex;
        align-items: center;
        justify-content: space-between;
        width: 100%;
    
    }

    .container-pages{
        margin-right: 30px;
    }

    /* @import url('https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@400;700;800&display=swap'); */

    .container-pages a{
        color: rgb(245, 242, 242);
        margin-right: 25px;
        text-decoration: none;
        text-transform: uppercase;
        font-family: 'M PLUS Rounded 1c', sans-serif;
        font-weight: 600;
        font-size: 14px;
    }

</style>    