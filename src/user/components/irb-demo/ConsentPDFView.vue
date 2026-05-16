<script setup>
import { ref } from 'vue'
import useViewAPI from '@/core/composables/useViewAPI'
import { Button } from '@/uikit/components/ui/button'
import { Switch } from '@/uikit/components/ui/switch'
import { Label } from '@/uikit/components/ui/label'

const api = useViewAPI()
const consented = ref(false)

function proceed() {
  api.goNextView()
}
</script>

<template>
  <div class="flex w-full" style="height: 100vh;">
    <div class="w-3/5 h-full border-r border-border">
      <iframe src="/consent-form.pdf" class="w-full h-full" style="display:block;" />
    </div>
    <div class="w-2/5 flex flex-col justify-center items-start px-10 gap-6">
      <h2 class="text-xl font-bold leading-snug">
        We first must verify that you are participating willingly and know your rights.
      </h2>
      <p class="text-muted-foreground text-sm">
        Please take the time to read the consent form (you can scroll the page).
      </p>
      <div class="flex items-center gap-3">
        <Switch id="consent" v-model:checked="consented" />
        <Label for="consent" class="text-sm cursor-pointer">I consent and am over 18 years old.</Label>
      </div>
      <Button :disabled="!consented" @click="proceed">
        Let's start <i-fa6-solid-arrow-right class="ml-2" />
      </Button>
    </div>
  </div>
</template>
