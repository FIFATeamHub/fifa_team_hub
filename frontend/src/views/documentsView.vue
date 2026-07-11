<template>
    <div class="documents-view">
        <DocumentsList />
    </div>
</template>

<script setup lang="ts">

import DocumentsList from '@/components/documents/DocumentsList.vue'

</script>

<style scoped>

.documents-view {
    min-height: 100vh;
    max-width: var(--max-width);
    margin: 0 auto;
    padding: var(--padding-section) var(--padding-page-x);
    background-color: var(--color-bg-base);
}

</style>
