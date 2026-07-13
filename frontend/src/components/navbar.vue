<template>
    <header class="navbar">
        <div class="navbar__inner">

            <RouterLink to="/dashboard" class="navbar__brand">
                <img class="navbar__logo" src="/img/logo-copa-branca-removebg.png" alt="Logo da FIFA Team Hub">
                <span class="navbar__brand-title">FIFA <span class="navbar__brand-highlight">TEAM HUB</span></span>
            </RouterLink>

            <nav class="navbar__links">
                <RouterLink to="/documentos" class="navbar__link">Documentos</RouterLink>
                <RouterLink to="/upload" class="navbar__link">Upload</RouterLink>
                <RouterLink
                    v-if="authStore.user?.role === 'AUDITOR' || authStore.user?.role === 'ORGANIZER'"
                    to="/audit"
                    class="navbar__link"
                >
                    Auditoria
                </RouterLink>
            </nav>

            <div class="navbar__user" ref="userMenuRef">
                <button type="button" class="navbar__user-trigger" @click="toggleMenu">
                    <span class="navbar__user-avatar">{{ userInitials }}</span>
                    <span class="navbar__user-info">
                        <span class="navbar__user-name">{{ authStore.user?.full_name || 'Usuário' }}</span>
                        <span class="navbar__user-role">{{ userRoleLabel }}</span>
                    </span>
                    <svg class="navbar__user-chevron" :class="{ 'navbar__user-chevron--open': isMenuOpen }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M6 9l6 6 6-6" />
                    </svg>
                </button>

                <div v-if="isMenuOpen" class="navbar__dropdown">
                    <button type="button" class="navbar__logout" @click="handleLogout">Sair do sistema</button>
                </div>
            </div>

        </div>
    </header>
</template>

<script setup lang="ts">

import { ref, computed, onMounted, onUnmounted } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'

defineOptions({ name: 'AppNavbar' })

const authStore = useAuthStore()
const router = useRouter()

const roleLabels: Record<string, string> = {
    ATHELETE: 'Jogador',
    TECHNICAL_STAFF: 'Comissão Técnica',
    MEDICAL_STAFF: 'Comissão Médica',
    AUDITOR: 'Auditor',
    ORGANIZER: 'Organizador'
}

const userInitials = computed(() => {
    const name = authStore.user?.full_name
    if (!name) return ''
    const partes = name.trim().split(/\s+/).filter(Boolean)
    const primeira = partes[0]?.[0] ?? ''
    const ultima = partes.length > 1 ? partes[partes.length - 1][0] : ''
    return (primeira + ultima).toUpperCase()
})

const userRoleLabel = computed(() => {
    const role = authStore.user?.role
    return roleLabels[role] ?? role ?? ''
})

const isMenuOpen = ref(false)
const userMenuRef = ref<HTMLElement | null>(null)

function toggleMenu() {
    isMenuOpen.value = !isMenuOpen.value
}

function handleClickOutside(event: MouseEvent) {
    if (userMenuRef.value && !userMenuRef.value.contains(event.target as Node)) {
        isMenuOpen.value = false
    }
}

async function handleLogout() {
    await authStore.logout()
    router.push('/login')
    isMenuOpen.value = false
}

onMounted(() => document.addEventListener('click', handleClickOutside))
onUnmounted(() => document.removeEventListener('click', handleClickOutside))

</script>

<style scoped>

.navbar {
    position: sticky;
    top: 0;
    z-index: var(--z-navbar);
    background-color: var(--color-surface-navbar);
    border-bottom: 1px solid var(--color-border-default);
}

.navbar__inner {
    max-width: var(--max-width);
    height: var(--navbar-height);
    margin: 0 auto;
    padding: 0 var(--padding-page-x);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-6);
}

.navbar__brand {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    text-decoration: none;
}

.navbar__logo {
    width: auto;
    height: 32px;
}

.navbar__brand-title {
    font-family: var(--font-heading);
    font-weight: var(--font-weight-black);
    font-size: var(--font-size-h3);
    letter-spacing: var(--letter-spacing-heading);
    text-transform: uppercase;
    color: var(--color-text-primary);
}

.navbar__brand-highlight {
    color: var(--color-gold);
}

.navbar__links {
    display: flex;
    align-items: center;
    gap: var(--space-8);
    height: 100%;
}

.navbar__link {
    display: flex;
    align-items: center;
    height: 100%;
    font-family: var(--font-body);
    font-weight: var(--font-weight-semibold);
    font-size: calc(var(--font-size-body) * 1.2);
    color: var(--color-text-secondary);
    text-decoration: none;
    border-bottom: 2px solid transparent;
    transition: color var(--transition-default), border-color var(--transition-default);
}

.navbar__link:hover {
    color: var(--color-text-primary);
}

.navbar__link.router-link-active {
    color: var(--color-text-primary);
    border-bottom-color: var(--color-gold);
}

.navbar__user {
    position: relative;
}

.navbar__user-trigger {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-2);
    background: none;
    border: none;
    border-radius: var(--radius-sm);
    cursor: pointer;
    transition: background-color var(--transition-default);
}

.navbar__user-trigger:hover {
    background-color: var(--color-surface-elevated);
}

.navbar__user-avatar {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    border: 1px solid var(--color-border-gold);
    border-radius: var(--radius-full);
    background-color: var(--color-warning-bg);
    color: var(--color-gold);
    font-family: var(--font-mono);
    font-weight: var(--font-weight-bold);
    font-size: var(--font-size-small);
}

.navbar__user-info {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    line-height: 1.3;
}

.navbar__user-name {
    font-family: var(--font-body);
    font-weight: var(--font-weight-semibold);
    font-size: var(--font-size-small);
    color: var(--color-text-primary);
}

.navbar__user-role {
    font-family: var(--font-mono);
    font-size: var(--font-size-label);
    letter-spacing: var(--letter-spacing-label);
    text-transform: uppercase;
    color: var(--color-text-tertiary);
}

.navbar__user-chevron {
    width: 16px;
    height: 16px;
    color: var(--color-text-tertiary);
    transition: transform var(--transition-default);
}

.navbar__user-chevron--open {
    transform: rotate(180deg);
}

.navbar__dropdown {
    position: absolute;
    top: calc(100% + var(--space-2));
    right: 0;
    min-width: 180px;
    background-color: var(--color-surface-elevated);
    border: 1px solid var(--color-border-default);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-card);
    padding: var(--space-2);
    z-index: var(--z-dropdown);
}

.navbar__logout {
    width: 100%;
    text-align: left;
    padding: var(--space-2) var(--space-3);
    background: none;
    border: none;
    border-radius: var(--radius-sm);
    color: var(--color-danger);
    font-family: var(--font-body);
    font-weight: var(--font-weight-semibold);
    font-size: var(--font-size-small);
    cursor: pointer;
    transition: background-color var(--transition-default);
}

.navbar__logout:hover {
    background-color: var(--color-danger-bg);
}

@media (max-width: 720px) {
    .navbar__links {
        gap: var(--space-4);
    }

    .navbar__user-info {
        display: none;
    }
}

</style>
