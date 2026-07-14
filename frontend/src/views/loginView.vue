<template>
    <div class="login-view">

        <section class="login-view__hero">
            <div class="login-view__hero-bg"></div>
            <div class="login-view__hero-overlay"></div>
            <div class="login-view__hero-edge"></div>

            <div class="login-view__hero-content">
                <div class="login-view__brand">
                    <img src="/img/logo-copa-branca-removebg.png" alt="Escudo FIFA Team Hub" class="login-view__brand-logo">
                    <span class="login-view__brand-divider"></span>
                    <h1 class="login-view__brand-title">FIFA <span class="login-view__brand-highlight">TEAM HUB</span></h1>
                </div>

                <div class="login-view__headline">
                    <p class="login-view__headline-line login-view__headline-line--primary">Gerencie o presente</p>
                    <p class="login-view__headline-line login-view__headline-line--muted">Conquiste o amanhã</p>
                    <p class="login-view__headline-line login-view__headline-line--accent">Rumo à glória.</p>
                </div>
            </div>

            <p class="login-view__footer">© {{ currentYear }} FIFA Team Hub · Todos os direitos reservados</p>
        </section>

        <section class="login-view__panel">
            <LoginForm />
        </section>

    </div>
</template>

<script setup lang="ts">

import LoginForm from '@/components/loginForm.vue'

const currentYear = new Date().getFullYear()

</script>

<style scoped>

.login-view {
    display: flex;
    min-height: 100vh;
    background-color: var(--color-bg-deep);
}

.login-view__hero {
    position: relative;
    flex: 1 1 60%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    overflow: hidden;
    padding: var(--space-12) var(--space-14);
}

.login-view__hero-content {
    display: flex;
    flex-direction: column;
    gap: var(--space-10);
}

.login-view__hero-bg {
    position: absolute;
    inset: 0;
    background-image: url('/img/login-hero.png');
    background-size: cover;
    background-position: center;
    z-index: 0;
}

.login-view__hero-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg,
        color-mix(in srgb, var(--color-bg-base) 82%, transparent) 0%,
        color-mix(in srgb, var(--color-bg-base) 55%, transparent) 50%,
        color-mix(in srgb, var(--color-bg-mid) 30%, transparent) 100%);
    z-index: 1;
}

.login-view__hero-edge {
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

.login-view__brand {
    position: relative;
    z-index: 2;
    display: flex;
    align-items: center;
    gap: var(--space-4);
}

.login-view__brand-logo {
    width: auto;
    height: calc(var(--font-size-h2) * 2.3);
}

.login-view__brand-divider {
    width: 1px;
    height: 32px;
    background-color: var(--color-border-default);
}

.login-view__brand-title {
    font-family: var(--font-heading);
    font-weight: var(--font-weight-black);
    font-size: calc(var(--font-size-h2) * 1.3);
    letter-spacing: var(--letter-spacing-heading);
    text-transform: uppercase;
    color: var(--color-text-primary);
}

.login-view__brand-highlight {
    color: var(--color-gold);
}

.login-view__headline {
    position: relative;
    z-index: 2;
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
    padding-left: var(--space-6);
    border-left: 2px solid var(--color-gold);
}

.login-view__headline-line {
    font-family: var(--font-heading);
    font-weight: var(--font-weight-black);
    font-size: calc(var(--font-size-h1) * 0.8);
    letter-spacing: var(--letter-spacing-tight);
    line-height: var(--line-height-display);
    text-transform: uppercase;
}

.login-view__headline-line--primary {
    color: var(--color-text-primary);
}

.login-view__headline-line--muted {
    color: var(--color-text-muted);
}

.login-view__headline-line--accent {
    color: var(--color-gold);
}

.login-view__footer {
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

.login-view__panel {
    flex: 0 0 44%;
    min-width: 420px;
    display: flex;
    background-color: var(--color-bg-base);
    border-left: 1px solid var(--color-border-default);
}

@media (max-width: 900px) {
    .login-view {
        flex-direction: column;
    }

    .login-view__hero {
        flex: none;
        min-height: 45vh;
        padding: var(--space-8);
    }

    .login-view__panel {
        flex: none;
        min-width: unset;
        border-left: none;
        border-top: 1px solid var(--color-border-default);
    }
}

</style>
