
<template>
    <div class="register-view">

        <section class="register-view__hero">
            <div class="register-view__hero-bg"></div>
            <div class="register-view__hero-overlay"></div>
            <div class="register-view__hero-edge"></div>

            <div class="register-view__hero-content">
                <div class="register-view__brand">
                    <img src="/img/logo-copa-branca-removebg.png" alt="Escudo FIFA Team Hub" class="register-view__brand-logo">
                    <span class="register-view__brand-divider"></span>
                    <h1 class="register-view__brand-title">FIFA <span class="register-view__brand-highlight">TEAM HUB</span></h1>
                </div>

                <div class="register-view__headline">
                    <p class="register-view__headline-line register-view__headline-line--primary">Gerencie o presente</p>
                    <p class="register-view__headline-line register-view__headline-line--muted">Conquiste o amanhã</p>
                    <p class="register-view__headline-line register-view__headline-line--accent">Rumo à glória.</p>
                </div>
            </div>

            <p class="register-view__footer">© {{ currentYear }} FIFA Team Hub · Todos os direitos reservados</p>
        </section>

        <section class="register-view__panel">
            <cadastroForm/>
        </section>

    </div>
</template>

<script setup lang="ts">

import cadastroForm from '@/components/cadastroForm.vue'

const currentYear = new Date().getFullYear()

</script>

<style scoped>

.register-view {
    display: flex;
    min-height: 100vh;
    background-color: var(--color-bg-deep);
}

.register-view__hero {
    position: relative;
    flex: 1 1 60%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    overflow: hidden;
    padding: var(--space-12) var(--space-14);
}

.register-view__hero-content {
    display: flex;
    flex-direction: column;
    gap: var(--space-10);
}

.register-view__hero-bg {
    position: absolute;
    inset: 0;
    background-image: url('/img/login-hero.png');
    background-size: cover;
    background-position: center;
    z-index: 0;
}

.register-view__hero-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg,
        color-mix(in srgb, var(--color-bg-base) 82%, transparent) 0%,
        color-mix(in srgb, var(--color-bg-base) 55%, transparent) 50%,
        color-mix(in srgb, var(--color-bg-mid) 30%, transparent) 100%);
    z-index: 1;
}

.register-view__hero-edge {
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

.register-view__brand {
    position: relative;
    z-index: 2;
    display: flex;
    align-items: center;
    gap: var(--space-4);
}

.register-view__brand-logo {
    width: auto;
    height: calc(var(--font-size-h2) * 2.3);
}

.register-view__brand-divider {
    width: 1px;
    height: 32px;
    background-color: var(--color-border-default);
}

.register-view__brand-title {
    font-family: var(--font-heading);
    font-weight: var(--font-weight-black);
    font-size: calc(var(--font-size-h2) * 1.3);
    letter-spacing: var(--letter-spacing-heading);
    text-transform: uppercase;
    color: var(--color-text-primary);
}

.register-view__brand-highlight {
    color: var(--color-gold);
}

.register-view__headline {
    position: relative;
    z-index: 2;
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
    padding-left: var(--space-6);
    border-left: 2px solid var(--color-gold);
}

.register-view__headline-line {
    font-family: var(--font-heading);
    font-weight: var(--font-weight-black);
    font-size: calc(var(--font-size-h1) * 0.8);
    letter-spacing: var(--letter-spacing-tight);
    line-height: var(--line-height-display);
    text-transform: uppercase;
}

.register-view__headline-line--primary {
    color: var(--color-text-primary);
}

.register-view__headline-line--muted {
    color: var(--color-text-muted);
}

.register-view__headline-line--accent {
    color: var(--color-gold);
}

.register-view__footer {
    position: absolute;
    left: var(--space-14);
    bottom: var(--space-12);
    z-index: 2;
    font-family: var(--font-mono);
    font-size: var(--font-size-label);
    letter-spacing: var(--letter-spacing-mono);
    text-transform: uppercase;
    color: var(--color-text-muted);
}

.register-view__panel {
    flex: 0 0 44%;
    min-width: 420px;
    display: flex;
    background-color: var(--color-bg-base);
    border-left: 1px solid var(--color-border-default);
    overflow-y: auto;
}

@media (max-width: 900px) {
    .register-view {
        flex-direction: column;
    }

    .register-view__hero {
        flex: none;
        min-height: 45vh;
        padding: var(--space-8);
    }

    .register-view__panel {
        flex: none;
        min-width: unset;
        border-left: none;
        border-top: 1px solid var(--color-border-default);
    }
}

</style>
