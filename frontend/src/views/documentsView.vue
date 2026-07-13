<template>
    <div class="documents-view">

        <section class="documents-view__hero">
            <div class="documents-view__hero-bg"></div>
            <div class="documents-view__hero-overlay"></div>
            <div class="documents-view__hero-edge"></div>
            <h1 class="documents-view__hero-title">
                Visualização
                <span class="documents-view__hero-title--muted">de documentos</span>
            </h1>
        </section>

        <div class="documents-view__content">
            <DocumentsList />
        </div>

    </div>
</template>

<script setup lang="ts">

import DocumentsList from '@/components/documents/DocumentsList.vue'

</script>

<style scoped>

.documents-view {
    min-height: 100vh;
    background-color: var(--color-bg-base);
}

.documents-view__hero {
    position: relative;
    overflow: hidden;
    padding: var(--space-14) var(--padding-page-x);
    background-color: var(--color-bg-base);
}

.documents-view__hero-bg {
    position: absolute;
    inset: 0;
    background-image: url('/img/documents-hero.png');
    background-size: cover;
    background-position: center;
    z-index: 0;
}

.documents-view__hero-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg,
        color-mix(in srgb, var(--color-bg-base) 85%, transparent) 0%,
        color-mix(in srgb, var(--color-bg-base) 60%, transparent) 55%,
        color-mix(in srgb, var(--color-bg-mid) 35%, transparent) 100%);
    z-index: 1;
}

.documents-view__hero-edge {
    position: absolute;
    right: 0;
    bottom: 0;
    left: 0;
    height: 1px;
    background: linear-gradient(90deg,
        color-mix(in srgb, var(--color-gold) 50%, transparent),
        color-mix(in srgb, var(--color-gold) 20%, transparent),
        transparent);
    z-index: 2;
}

.documents-view__hero-title {
    position: relative;
    z-index: 3;
    max-width: var(--max-width);
    margin: 0 auto;
    font-family: var(--font-heading);
    font-weight: var(--font-weight-black);
    font-size: var(--font-size-display);
    letter-spacing: var(--letter-spacing-tight);
    line-height: var(--line-height-display);
    color: var(--color-text-primary);
}

.documents-view__hero-title--muted {
    display: block;
    color: var(--color-text-muted);
}

.documents-view__content {
    max-width: var(--max-width);
    margin: 0 auto;
    padding: var(--padding-section) var(--padding-page-x);
}

</style>
