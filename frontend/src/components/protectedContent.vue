<script setup lang="ts">

import { usePermissions } from '@/composables/usePermissions'

const { permission, dataTeamId } = defineProps({
    permission: String,
    dataTeamId: {
        type: String,
        default: null
    }
})

const { can } = usePermissions();

</script>


<template>

    <slot v-if="can(permission, dataTeamId)"></slot>

</template>