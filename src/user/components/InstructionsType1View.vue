<script setup>
import { ref, computed } from 'vue'
import useViewAPI from '@/core/composables/useViewAPI'
import { Button } from '@/uikit/components/ui/button'
import { ConstrainedTaskWindow } from '@/uikit/layouts'

const api = useViewAPI()

const page = ref(0)
const TOTAL_PAGES = 4 // 0=intro, 1=example1, 2=example2, 3=example3

const sliderValues = ref([5, 5, 5])
const sliderTouched = ref([false, false, false])

const currentSlider = computed({
  get: () => sliderValues.value[page.value - 1],
  set: (v) => {
    sliderValues.value[page.value - 1] = v
    sliderTouched.value[page.value - 1] = true
  },
})

const examples = [
  {
    label: 'Example 1 of 3 — Simple expression',
    expression: '3 + 4 × 5',
    traceLines: ['3 + 4 × 5', '↓', '7 × 5', '↓', '35'],
    description: 'Did addition before multiplication.',
    descriptionAccurate: true,
    hint: 'The student got 35 instead of the correct answer (23). The description correctly captures the rule they applied — they treated addition as higher priority than multiplication.',
  },
  {
    label: 'Example 2 of 3 — Expression with brackets',
    expression: '(3 + 4) × 5',
    traceLines: ['(3 + 4) × 5', '↓', '7 × 5', '↓', '35'],
    description: 'Evaluated brackets first, then multiplied.',
    descriptionAccurate: true,
    hint: 'The student got the right answer (35). The description accurately captures the rule they followed — brackets first, then multiplication.',
  },
  {
    label: 'Example 3 of 3 — Inaccurate description',
    expression: '2 + 3 × 4',
    traceLines: ['2 + 3 × 4', '↓', '5 × 4', '↓', '20'],
    description: 'Multiplied before adding.',
    descriptionAccurate: false,
    hint: 'The student actually added first and got 20 (the correct answer is 14). The description says they multiplied first — but that\'s the opposite of what they did. This is an inaccurate description.',
  },
]

const currentExample = computed(() => examples[page.value - 1])

function next() {
  if (page.value < TOTAL_PAGES - 1) {
    page.value++
  } else {
    api.goFirstStep()
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
    <div class="flex flex-col gap-5 px-8 py-6 w-full max-w-2xl mx-auto h-full overflow-y-auto">

      <!-- ── Page 0: Introduction ──────────────────────────────────────────── -->
      <template v-if="page === 0">
        <h1 class="text-2xl font-bold">Instructions</h1>

        <p class="text-base leading-relaxed">
          This study looks at whether participants can examine a student's step-by-step working
          through a math equation and identify what rules or ideas the student may have
          misconceptions about.
        </p>

        <p class="text-base leading-relaxed">
          In each trial, you will see:
        </p>
        <ul class="list-disc pl-6 text-base leading-relaxed space-y-1">
          <li>A math expression that was given to a third-grade student</li>
          <li>The student's step-by-step working and final answer</li>
          <li>A proposed explanation of what the student did or what misconception they have</li>
        </ul>

        <p class="text-base leading-relaxed">
          Your job is to <strong>rate how accurate the explanation is</strong>, using a slider
          from <strong>0 to 10</strong>:
        </p>
        <div class="bg-muted rounded-lg px-5 py-4 text-sm space-y-1">
          <p><span class="font-semibold">0</span> — The explanation is completely inaccurate; it does not describe what the student did at all.</p>
          <p><span class="font-semibold">5</span> — The explanation is partially accurate.</p>
          <p><span class="font-semibold">10</span> — The explanation is perfectly accurate; it describes exactly what the student did.</p>
        </div>

        <p class="text-base leading-relaxed">
          The next few screens will walk you through three examples so you can get a feel for the task.
        </p>

        <div class="flex justify-end pt-2">
          <Button @click="next()">See examples <i-fa6-solid-arrow-right class="ml-1" /></Button>
        </div>
      </template>

      <!-- ── Pages 1–3: Interactive examples ──────────────────────────────── -->
      <template v-else>
        <div class="text-xs uppercase tracking-wide text-muted-foreground font-medium">
          {{ currentExample.label }}
        </div>

        <!-- Expression -->
        <div>
          <p class="text-sm text-muted-foreground mb-1">Expression given to the student:</p>
          <p class="text-2xl font-mono font-semibold">{{ currentExample.expression }}</p>
        </div>

        <!-- Trace -->
        <div>
          <p class="text-sm text-muted-foreground mb-2">Student's working:</p>
          <div class="bg-muted rounded-lg p-4 font-mono text-sm leading-7 whitespace-pre">
            <div v-for="(line, i) in currentExample.traceLines" :key="i">
              <span v-if="line === '↓'" class="text-muted-foreground">  =</span>
              <span v-else>{{ line }}</span>
            </div>
          </div>
        </div>

        <!-- Description -->
        <div class="rounded-lg px-4 py-3 text-sm"
          :class="currentExample.descriptionAccurate
            ? 'bg-amber-50 border border-amber-200 text-amber-900'
            : 'bg-amber-50 border border-amber-200 text-amber-900'"
        >
          <p class="font-medium mb-1">Proposed explanation:</p>
          <p class="italic">"{{ currentExample.description }}"</p>
        </div>

        <!-- Slider -->
        <div class="flex flex-col gap-2 px-1">
          <p class="text-sm font-medium">How accurate is this description?</p>
          <input
            type="range"
            min="0"
            max="10"
            step="1"
            v-model.number="currentSlider"
            class="w-full h-2 cursor-pointer accent-primary"
          />
          <div class="flex justify-between items-center text-xs">
            <span class="text-muted-foreground">0 — Not accurate at all</span>
            <span class="text-2xl font-bold text-foreground tabular-nums">{{ currentSlider }}</span>
            <span class="text-muted-foreground">10 — Perfectly accurate</span>
          </div>
        </div>

        <!-- Feedback popup when slider is touched -->
        <div
          v-if="sliderTouched[page - 1]"
          class="rounded-lg border px-4 py-3 text-sm transition-all"
          :class="currentExample.descriptionAccurate
            ? 'bg-blue-50 border-blue-200 text-blue-900'
            : 'bg-red-50 border-red-200 text-red-900'"
        >
          <p>
            So you think this description is
            <span class="font-bold">{{ currentSlider }}</span> / 10 accurate.
          </p>
          <p class="mt-2 text-xs opacity-80">{{ currentExample.hint }}</p>
        </div>

        <!-- Nav -->
        <div class="flex justify-between pt-2">
          <Button variant="outline" @click="page--">
            <i-fa6-solid-arrow-left class="mr-1" /> Back
          </Button>
          <Button @click="next()">
            {{ page < TOTAL_PAGES - 1 ? 'Next example' : 'Start the task' }}
            <i-fa6-solid-arrow-right class="ml-1" />
          </Button>
        </div>
      </template>

    </div>
  </ConstrainedTaskWindow>
</template>
