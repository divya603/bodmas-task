<script setup>
import useViewAPI from '@/core/composables/useViewAPI'
import { Button } from '@/uikit/components/ui/button'

const api = useViewAPI()
const baseURL = import.meta.env.BASE_URL

function finish() {
  api.goNextView()
}
</script>

<template>
  <div class="flex w-full" style="height: 100vh;">
    <div class="w-3/5 h-full border-r border-border">
      <iframe :src="`${baseURL}debrief.pdf`" class="w-full h-full" style="display:block;" />
    </div>
    <div class="w-2/5 flex flex-col justify-center items-start px-10 gap-6">
      <h2 class="text-xl font-bold leading-snug">
        Thank you for participating!
      </h2>
      <p class="text-muted-foreground text-sm">
        Please take a moment to read the debrief form on the left.
      </p>
      <Button @click="finish">
        Done <i-fa6-solid-arrow-right class="ml-2" />
      </Button>
    </div>
  </div>
</template>
