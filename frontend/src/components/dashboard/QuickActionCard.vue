<script setup lang="ts">
defineProps<{
    title: string
    subtitle: string
    to?: string
    comingSoon?: boolean
}>()

const emit = defineEmits<{
    (e: 'activate'): void
}>()
</script>

<template>

    <RouterLink
        v-if="to && !comingSoon"
        :to="to"
        class="quick-action"
    >
        <span class="quick-action__decor" aria-hidden="true"></span>
        <span class="quick-action__icon"><slot name="icon" /></span>
        <h3 class="quick-action__title">{{ title }}</h3>
        <p class="quick-action__subtitle">{{ subtitle }}</p>
        <span class="quick-action__cta">
            Abrir
            <svg viewBox="0 0 24 24" fill="currentColor" stroke="none">
                <path d="M13 2 4 14h6l-1 8 9-12h-6l1-8Z" />
            </svg>
        </span>
    </RouterLink>

    <button
        v-else-if="!comingSoon"
        type="button"
        class="quick-action"
        @click="emit('activate')"
    >
        <span class="quick-action__decor" aria-hidden="true"></span>
        <span class="quick-action__icon"><slot name="icon" /></span>
        <h3 class="quick-action__title">{{ title }}</h3>
        <p class="quick-action__subtitle">{{ subtitle }}</p>
        <span class="quick-action__cta">
            Abrir
            <svg viewBox="0 0 24 24" fill="currentColor" stroke="none">
                <path d="M13 2 4 14h6l-1 8 9-12h-6l1-8Z" />
            </svg>
        </span>
    </button>

    <div v-else class="quick-action quick-action--soon">
        <span class="quick-action__decor" aria-hidden="true"></span>
        <span class="quick-action__icon"><slot name="icon" /></span>
        <h3 class="quick-action__title">{{ title }}</h3>
        <p class="quick-action__subtitle">{{ subtitle }}</p>
        <span class="quick-action__badge">Em breve</span>
    </div>

</template>

<style scoped>

.quick-action {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-2);
    padding: var(--padding-card);
    background-color: var(--color-surface-primary);
    border: 1px solid var(--color-border-default);
    border-radius: var(--radius-xl);
    box-shadow: var(--shadow-card);
    overflow: hidden;
    text-align: left;
    width: 100%;
    transition: transform var(--transition-default), border-color var(--transition-default);
}

a.quick-action,
button.quick-action {
    cursor: pointer;
}

a.quick-action:hover,
button.quick-action:hover {
    transform: translateY(-4px);
    border-color: var(--color-border-gold);
}

.quick-action--soon {
    cursor: default;
}

.quick-action__decor {
    position: absolute;
    top: calc(var(--space-8) * -1);
    right: calc(var(--space-8) * -1);
    width: 96px;
    height: 96px;
    border-radius: var(--radius-full);
    background-color: var(--color-gold-dim);
}

.quick-action__icon {
    position: relative;
    z-index: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 44px;
    height: 44px;
    margin-bottom: var(--space-2);
    background-color: var(--color-warning-bg);
    border: 1px solid var(--color-border-gold);
    border-radius: var(--radius-md);
    color: var(--color-gold);
}

.quick-action__icon :deep(svg) {
    width: 22px;
    height: 22px;
}

.quick-action__title {
    position: relative;
    z-index: 1;
    font-family: var(--font-heading);
    font-weight: var(--font-weight-black);
    font-size: var(--font-size-h3);
    letter-spacing: var(--letter-spacing-heading);
    color: var(--color-text-primary);
}

.quick-action__subtitle {
    position: relative;
    z-index: 1;
    font-family: var(--font-body);
    font-size: var(--font-size-small);
    color: var(--color-text-tertiary);
}

.quick-action__cta {
    display: inline-flex;
    align-items: center;
    gap: var(--space-1);
    margin-top: var(--space-3);
    font-family: var(--font-mono);
    font-size: var(--font-size-label);
    font-weight: var(--font-weight-bold);
    letter-spacing: var(--letter-spacing-label);
    text-transform: uppercase;
    color: var(--color-gold);
}

.quick-action__cta svg {
    width: 14px;
    height: 14px;
}

.quick-action__badge {
    margin-top: var(--space-3);
    padding: var(--space-1) var(--space-3);
    background-color: var(--color-surface-elevated);
    border: 1px solid var(--color-border-default);
    border-radius: var(--radius-full);
    font-family: var(--font-mono);
    font-size: var(--font-size-label);
    letter-spacing: var(--letter-spacing-label);
    text-transform: uppercase;
    color: var(--color-text-tertiary);
}

</style>