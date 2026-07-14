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

            <DocumentsList ref="documentsListRef">
                <template v-if="can('upload:documents')" #toolbar-actions>
                    <button class="documents-view__upload-btn" @click="isModalOpen = true">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M12 15V4m0 0-4 4m4-4 4 4" stroke-linecap="round" stroke-linejoin="round" />
                            <path d="M4 15v3a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-3" stroke-linecap="round" stroke-linejoin="round" />
                        </svg>
                        Enviar Documento
                    </button>
                </template>
            </DocumentsList>
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
import DocumentsList from '@/components/documents/DocumentsList.vue'
import UploadDocumentModal from '@/components/documents/UploadDocumentModal.vue'
import { usePermissions } from '@/composables/usePermissions'

const { can } = usePermissions()

const isModalOpen = ref(false)
const documentsListRef = ref<InstanceType<typeof DocumentsList> | null>(null)

function handleUploadSuccess() {
    isModalOpen.value = false
    documentsListRef.value?.refresh()
}

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

.documents-view__upload-btn {
    display: inline-flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-3) var(--space-6);
    background-color: var(--color-gold);
    border: none;
    border-radius: var(--radius-full);
    color: var(--color-bg-deep);
    font-family: var(--font-body);
    font-weight: var(--font-weight-black);
    font-size: var(--font-size-body);
    cursor: pointer;
    box-shadow: var(--shadow-card);
    transition: background-color var(--transition-default), box-shadow var(--transition-default), transform var(--transition-default);
}

.documents-view__upload-btn svg {
    width: 16px;
    height: 16px;
}

.documents-view__upload-btn:hover {
    background-color: var(--color-gold-hover);
    box-shadow: var(--shadow-glow-gold);
    transform: translateY(-2px);
}

</style>
