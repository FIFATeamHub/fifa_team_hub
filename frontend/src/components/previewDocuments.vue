<script setup>
async function previewDocument(docId: string) {
  const url = await getDownloadUrl(docId)
  
  // Abrir em nova aba
  window.open(url, '_blank')
}
</script>
 
<template>
  <button @click="previewDocument(doc.id)">👁️ Visualizar</button>
</template>