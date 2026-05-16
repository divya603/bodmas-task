<script setup>
import { ref, computed } from 'vue'
import useViewAPI from '@/core/composables/useViewAPI'
import { Button } from '@/uikit/components/ui/button'
import { ConstrainedTaskWindow } from '@/uikit/layouts'

const api = useViewAPI()

const trial = {
  studentName: 'Emily',
  expression: '2×(3+(4×5))',
  traceLines: ['2×(3+(4×5))', '↓', '2×(3+4)×5', '↓', '2×7×5', '↓', '14×5', '↓', '70'],
  learnerAns: '70',
  expertAns: '46',
  descriptionShown: 'skip the inner brackets and evaluate from the outside in',
}

const displayedLines = computed(() =>
  trial.traceLines.filter(l => l !== '↓')
)

const phase = ref(1)  // 1 = show trace + open response, 2 = show belief + rating
const textResponse = ref('')
const rating = ref(null)

const SCALE = [
  { value: 1, label: 'Strongly\nDisagree' },
  { value: 2, label: 'Disagree' },
  { value: 3, label: 'Neutral' },
  { value: 4, label: 'Agree' },
  { value: 5, label: 'Strongly\nAgree' },
]

function nextPhase() {
  if (phase.value === 1) {
    phase.value = 2
  } else {
    api.goNextView()
  }
}
</script>

<template>
  <ConstrainedTaskWindow
    variant="ghost"
    :responsiveUI="api.config.responsiveUI"
    :width="api.config.windowsizerRequest.width"
    :height="api.config.windowsizerRequest.height"
  >
    <div class="flex flex-col gap-4 p-4 text-left">

      <!-- Expression -->
      <div>
        <p class="text-xs text-muted-foreground mb-1">Expression given to {{ trial.studentName }}:</p>
        <p class="text-2xl font-mono font-semibold">{{ trial.expression }}</p>
      </div>

      <!-- Trace -->
      <div>
        <p class="text-xs text-muted-foreground mb-1">{{ trial.studentName }}'s working:</p>
        <div class="font-mono text-sm space-y-1">
          <div v-for="(line, i) in displayedLines" :key="i"
               :class="i === 0 ? 'text-muted-foreground' : (i === displayedLines.length - 1 ? 'font-bold' : '')">
            {{ i === 0 ? '' : '= ' }}{{ line }}
          </div>
        </div>
        <p class="text-xs text-muted-foreground mt-2">
          {{ trial.studentName }} got {{ trial.learnerAns }}
          (correct answer: {{ trial.expertAns }})
        </p>
      </div>

      <!-- Phase 1: open text -->
      <div v-if="phase === 1">
        <p class="text-sm font-medium mb-2">
          Does it seem like {{ trial.studentName }} misunderstands something, and if so, what?
        </p>
        <textarea
          v-model="textResponse"
          rows="3"
          class="w-full border border-border rounded-md p-2 text-sm resize-none focus:outline-none focus:ring-1 focus:ring-primary"
          placeholder="Write your thoughts here..."
        />
        <Button class="mt-3" :disabled="!textResponse.trim()" @click="nextPhase">
          Next <i-fa6-solid-arrow-right class="ml-2" />
        </Button>
      </div>

      <!-- Phase 2: belief statement + rating -->
      <div v-else class="flex flex-col gap-4">
        <div class="bg-amber-50 border border-amber-200 rounded-lg px-4 py-3 text-sm text-amber-900">
          <p class="italic">{{ trial.studentName }} believes they should {{ trial.descriptionShown }}.</p>
        </div>

        <div>
          <p class="text-sm font-medium mb-3">How well does this statement describe {{ trial.studentName }}'s belief?</p>
          <div class="flex justify-between gap-2">
            <button
              v-for="opt in SCALE"
              :key="opt.value"
              @click="rating = opt.value"
              class="flex-1 flex flex-col items-center gap-1 rounded-lg border-2 py-2 px-1 text-xs transition-colors"
              :class="rating === opt.value
                ? 'border-primary bg-primary/10 text-primary font-semibold'
                : 'border-border text-muted-foreground hover:border-primary/50'"
            >
              <span class="text-sm font-bold">{{ opt.value }}</span>
              <span class="text-center leading-tight whitespace-pre-line">{{ opt.label }}</span>
            </button>
          </div>
        </div>

        <Button :disabled="rating === null" @click="nextPhase">
          Finish <i-fa6-solid-arrow-right class="ml-2" />
        </Button>
      </div>

    </div>
  </ConstrainedTaskWindow>
</template>
