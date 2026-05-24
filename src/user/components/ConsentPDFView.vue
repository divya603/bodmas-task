<script setup>
import { ref, watch, onBeforeUnmount } from 'vue'
import { animate } from 'motion'
import appconfig from '@/core/config'
import { Button } from '@/uikit/components/ui/button'
import { Card, CardContent } from '@/uikit/components/ui/card'
import { Switch } from '@/uikit/components/ui/switch'
import { Label } from '@/uikit/components/ui/label'
import { TwoCol, ConstrainedPage } from '@/uikit/layouts'
import useViewAPI from '@/core/composables/useViewAPI'

const api = useViewAPI()

const baseURL = import.meta.env.BASE_URL
const pdfUrl = `${baseURL}consent-form.pdf`

function finish() {
  api.goNextView()
}

if (appconfig.anonymousMode) {
  finish()
}

const button = ref(null)
let timer

function wiggle() {
  if (api.persist.agree) {
    animate(button.value, { rotate: [0, 5, -5, 5, -5, 0] }, { duration: 1.25 }).finished.then(() => {
      timer = setTimeout(wiggle, 2000)
    })
  }
}

if (!('agree' in api.persist)) {
  api.persist.agree = ref(false)
}

if (api.persist.agree) {
  watch(api.persist.agree, (newVal) => {
    if (newVal) {
      timer = setTimeout(wiggle, 3000)
    }
  })
}

onBeforeUnmount(() => {
  clearTimeout(timer)
})
</script>

<template>
  <ConstrainedPage
    :responsiveUI="api.config.responsiveUI"
    :width="api.config.windowsizerRequest.width"
    :height="api.config.windowsizerRequest.height"
  >
    <TwoCol leftWidth="w-3/5" class="px-6">
      <template #left>
        <iframe
          :src="pdfUrl"
          class="w-full rounded border border-border"
          style="height: 850px;"
          title="Consent Form"
        />
      </template>

      <template #right>
        <Card class="bg-muted">
          <CardContent class="bg-muted">
            <p class="text-left font-semibold text-foreground mb-4">
              We first must verify that you are participating willingly and know your rights. Please take the time to
              read the consent form (you can scroll the page).
            </p>

            <div class="border-t border-gray-200 my-4"></div>

            <div class="flex items-center space-x-2 mb-4">
              <Switch
                variant="success"
                v-model="api.persist.agree"
                id="consent_toggle"
                name="consent_toggle"
                size="lg"
              />
              <Label for="consent_toggle" class="text-left text-sm font-medium">
                I consent and am over 18 years old.
              </Label>
            </div>

            <div class="mt-6">
              <Button
                ref="button"
                variant="success"
                size="lg"
                class="w-full"
                v-if="api.persist.agree"
                @click="finish()"
              >
                Let's start
                <svg class="w-4 h-4 ml-2" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fill-rule="evenodd"
                    d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z"
                    clip-rule="evenodd"
                  />
                </svg>
              </Button>
            </div>
          </CardContent>
        </Card>
      </template>
    </TwoCol>
  </ConstrainedPage>
</template>
