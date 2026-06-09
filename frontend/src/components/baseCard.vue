<template>

    <div class ="card">

        <slot></slot>

    </div>

</template>

<style scoped>

.card {
    background: #131221;
    width: 320px;
    padding: 40px;
    border-radius: 20px;
    display: flex;
    flex-direction: column;
    align-items: center;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
}

</style>