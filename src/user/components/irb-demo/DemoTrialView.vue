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

const LIKERT_OPTIONS = ['Strongly Agree', 'Agree', 'Somewhat Agree', 'Somewhat Disagree', 'Disagree', 'Strongly Disagree']

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
          <p class="text-sm font-medium mb-3">How much do you agree with this statement?</p>
          <div class="flex justify-between gap-2">
            <label
              v-for="option in [...LIKERT_OPTIONS].reverse()"
              :key="option"
              class="flex flex-col items-center gap-2 flex-1 cursor-pointer"
            >
              <input
                type="radio"
                :value="option"
                v-model="rating"
                class="accent-primary w-4 h-4"
              />
              <span class="text-xs text-center leading-tight text-muted-foreground">{{ option }}</span>
            </label>
          </div>
        </div>

        <Button :disabled="!rating" @click="nextPhase">
          Finish <i-fa6-solid-arrow-right class="ml-2" />
        </Button>
      </div>

    </div>
  </ConstrainedTaskWindow>
</template>
