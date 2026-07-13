<template>
    <div class="upload-view">

        <section class="upload-view__hero">
            <div class="upload-view__hero-bg"></div>
            <div class="upload-view__hero-overlay"></div>
            <div class="upload-view__hero-edge"></div>
            <h1 class="upload-view__hero-title">
                Envio
                <span class="upload-view__hero-title--muted">de documentos</span>
            </h1>
        </section>

        <div class="upload-view__content">

            <div v-if="can('upload:documents')" class="upload-view__panel">
                <p class="upload-view__panel-text">
                    Envie passaportes, laudos médicos, convocações, relatórios táticos ou esquemas de jogadas conforme seu perfil.
                </p>
                <button class="upload-view__upload-btn" @click="isModalOpen = true">
                    Enviar Documento
                </button>
            </div>

            <p v-else class="upload-view__empty">
                Seu perfil não possui permissão para enviar documentos.
            </p>

        </div>

        <UploadDocumentModal
            :isOpen="isModalOpen"
            :onClose="() => isModalOpen = false"
            :onSuccess="handleUploadSuccess"
        />

    </div>
</template>

<script setup lang="ts">

import { ref } from 'vue'
import { useRouter } from 'vue-router'
import UploadDocumentModal from '@/components/documents/UploadDocumentModal.vue'
import { usePermissions } from '@/composables/usePermissions'

const { can } = usePermissions()
const router = useRouter()

const isModalOpen = ref(false)

function handleUploadSuccess() {
    isModalOpen.value = false
    router.push('/documentos')
}

</script>

<style scoped>

.upload-view {
    min-height: 100vh;
    background-color: var(--color-bg-base);
}

.upload-view__hero {
    position: relative;
    overflow: hidden;
    padding: var(--space-14) var(--padding-page-x);
    background-color: var(--color-bg-base);
}

.upload-view__hero-bg {
    position: absolute;
    inset: 0;
    background-image: url('/img/documents-hero.png');
    background-size: cover;
    background-position: center;
    z-index: 0;
}

.upload-view__hero-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg,
        color-mix(in srgb, var(--color-bg-base) 85%, transparent) 0%,
        color-mix(in srgb, var(--color-bg-base) 60%, transparent) 55%,
        color-mix(in srgb, var(--color-bg-mid) 35%, transparent) 100%);
    z-index: 1;
}

.upload-view__hero-edge {
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

.upload-view__hero-title {
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

.upload-view__hero-title--muted {
    display: block;
    color: var(--color-text-muted);
}

.upload-view__content {
    max-width: var(--max-width);
    margin: 0 auto;
    padding: var(--padding-section) var(--padding-page-x);
}

.upload-view__panel {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-5);
    padding: var(--padding-card);
    background-color: var(--color-surface-primary);
    border: 1px solid var(--color-border-default);
    border-radius: var(--radius-xl);
    box-shadow: var(--shadow-card);
}

.upload-view__panel-text {
    max-width: 40rem;
    color: var(--color-text-secondary);
    font-family: var(--font-body);
    font-size: var(--font-size-body);
    line-height: var(--line-height-body);
}

.upload-view__upload-btn {
    padding: var(--space-3) var(--space-6);
    background-color: var(--color-gold);
    border: none;
    border-radius: var(--radius-sm);
    color: var(--color-bg-deep);
    font-family: var(--font-body);
    font-weight: var(--font-weight-black);
    font-size: var(--font-size-body);
    cursor: pointer;
    transition: background-color var(--transition-default);
}

.upload-view__upload-btn:hover {
    background-color: var(--color-gold-hover);
}

.upload-view__empty {
    padding: var(--space-8);
    text-align: center;
    color: var(--color-text-tertiary);
    font-family: var(--font-mono);
    font-size: var(--font-size-label);
    letter-spacing: var(--letter-spacing-mono);
    text-transform: uppercase;
}

</style>
