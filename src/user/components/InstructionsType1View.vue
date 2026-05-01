<script setup>
import { ref, computed } from 'vue'
import useViewAPI from '@/core/composables/useViewAPI'
import { Button } from '@/uikit/components/ui/button'
import { ConstrainedTaskWindow } from '@/uikit/layouts'

const api = useViewAPI()

const LIKERT_OPTIONS = ['Strongly Agree', 'Agree', 'Somewhat Agree', 'Somewhat Disagree', 'Disagree', 'Strongly Disagree']

const page = ref(0)
const TOTAL_PAGES = 7  // 0 = intro, then 2 pages per example × 3 examples

const demoTextResponses = ref(['', '', ''])
const demoSelections    = ref([null, null, null])

const examples = [
  {
    expression: '3 + 4 × 5',
    traceLines: ['3 + 4 × 5', '↓', '7 × 5', '↓', '35'],
    studentName: 'Alex',
    belief: 'do addition before multiplication',
    traceHiddenInPhase2: false,
  },
  {
    expression: '2 + 3 × 4',
    traceLines: ['2 + 3 × 4', '↓', '5 × 4', '↓', '20'],
    studentName: 'Sam',
    belief: 'work right to left when two operations have the same priority',
    traceHiddenInPhase2: false,
  },
  {
    expression: '(3 + 4) × 5',
    traceLines: ['(3 + 4) × 5', '↓', '7 × 5', '↓', '35'],
    studentName: 'Jordan',
    belief: 'ignore the brackets and compute as if they weren\'t there',
    traceHiddenInPhase2: true,
  },
]

// pages 1,2 → example 0; pages 3,4 → example 1; pages 5,6 → example 2
const exampleIndex  = computed(() => Math.floor((page.value - 1) / 2))
const isPhase1      = computed(() => page.value > 0 && (page.value - 1) % 2 === 0)
const currentExample = computed(() => examples[Math.max(0, exampleIndex.value)])

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
        <h1 class="text-2xl font-bold">📋 Instructions</h1>

        <p class="text-base leading-relaxed">
          You'll see math work from a series of different students 🧑‍🎓 and try to figure out what each one thinks about how math works. Each trial has two steps.
        </p>

        <div class="bg-muted rounded-lg px-5 py-4 text-sm space-y-4">
          <div>
            <p class="font-semibold mb-1">👀 Step 1</p>
            <p>You'll see a math expression and one student's step-by-step solution. Write your initial thoughts about what they did. ✏️</p>
          </div>
          <div>
            <p class="font-semibold mb-1">💭 Step 2</p>
            <p>You'll see a statement about what this student might believe. Rate it on this scale:</p>
            <div class="mt-2 space-y-1 pl-2">
              <p><span class="font-semibold">Strongly Agree</span> — perfectly describes their belief</p>
              <p><span class="font-semibold">Agree</span> — mostly matches</p>
              <p><span class="font-semibold">Somewhat Agree</span> — partly matches</p>
              <p><span class="font-semibold">Somewhat Disagree</span> — somewhat off</p>
              <p><span class="font-semibold">Disagree</span> — mostly off</p>
              <p><span class="font-semibold">Strongly Disagree</span> — doesn't describe them at all</p>
            </div>
          </div>
        </div>

        <p class="text-base leading-relaxed">
          ⚠️ In Step 2, the student's work may or may not still be visible. You won't know in advance!
        </p>

        <div class="flex justify-end pt-2">
          <Button @click="next()">Continue <i-fa6-solid-arrow-right class="ml-1" /></Button>
        </div>
      </template>

      <!-- ── Phase 1 (pages 1, 3, 5): expression + trace + text box ─────────── -->
      <template v-else-if="isPhase1">
        <div class="text-xs uppercase tracking-wide text-muted-foreground font-medium">
          Example {{ exampleIndex + 1 }} of 3 — Step 1
        </div>

        <div>
          <p class="text-sm text-muted-foreground mb-1">Expression given to {{ currentExample.studentName }}:</p>
          <p class="text-2xl font-mono font-semibold">{{ currentExample.expression }}</p>
        </div>

        <div>
          <p class="text-sm text-muted-foreground mb-2">{{ currentExample.studentName }}'s working:</p>
          <div class="bg-muted rounded-lg p-4 font-mono text-sm leading-7">
            <div v-for="(line, i) in currentExample.traceLines.filter(l => l !== '↓').slice(1)" :key="i">
              <span class="text-muted-foreground">= </span>{{ line }}
            </div>
          </div>
        </div>

        <div class="flex flex-col gap-2">
          <p class="text-sm font-medium">Does it seem like {{ currentExample.studentName }} misunderstands something, and if so, what?</p>
          <textarea
            v-model="demoTextResponses[exampleIndex]"
            placeholder="Type your thoughts here…"
            rows="3"
            class="w-full rounded-lg border border-input bg-background px-4 py-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>

        <div class="flex justify-between pt-2">
          <Button variant="outline" @click="page--"><i-fa6-solid-arrow-left class="mr-1" /> Back</Button>
          <Button :disabled="!demoTextResponses[exampleIndex].trim()" @click="next()">
            Continue <i-fa6-solid-arrow-right class="ml-1" />
          </Button>
        </div>
      </template>

      <!-- ── Phase 2 (pages 2, 4, 6): belief statement + Likert ────────────── -->
      <template v-else>
        <div class="text-xs uppercase tracking-wide text-muted-foreground font-medium">
          Example {{ exampleIndex + 1 }} of 3 — Step 2
          <span v-if="currentExample.traceHiddenInPhase2" class="ml-2 normal-case text-amber-700">(working no longer shown)</span>
        </div>

        <!-- Expression always shown -->
        <div>
          <p class="text-sm text-muted-foreground mb-1">Expression given to {{ currentExample.studentName }}:</p>
          <p class="text-2xl font-mono font-semibold">{{ currentExample.expression }}</p>
        </div>

        <!-- Trace only if not hidden -->
        <div v-if="!currentExample.traceHiddenInPhase2">
          <p class="text-sm text-muted-foreground mb-2">{{ currentExample.studentName }}'s working:</p>
          <div class="bg-muted rounded-lg p-4 font-mono text-sm leading-7">
            <div v-for="(line, i) in currentExample.traceLines.filter(l => l !== '↓').slice(1)" :key="i">
              <span class="text-muted-foreground">= </span>{{ line }}
            </div>
          </div>
        </div>

        <!-- Belief statement -->
        <div class="bg-amber-50 border border-amber-200 rounded-lg px-4 py-3 text-sm text-amber-900">
          <p class="italic">{{ currentExample.studentName }} believes they should {{ currentExample.belief }}.</p>
        </div>

        <!-- Likert -->
        <div class="flex flex-col gap-3">
          <p class="text-sm font-medium">How much do you agree with this statement?</p>
          <div class="flex justify-between gap-2">
            <label
              v-for="option in [...LIKERT_OPTIONS].reverse()"
              :key="option"
              class="flex flex-col items-center gap-2 flex-1 cursor-pointer"
            >
              <input type="radio" :value="option" v-model="demoSelections[exampleIndex]" class="accent-primary w-4 h-4" />
              <span class="text-xs text-center leading-tight text-muted-foreground">{{ option }}</span>
            </label>
          </div>
        </div>


        <div class="flex justify-between pt-2">
          <Button variant="outline" @click="page--"><i-fa6-solid-arrow-left class="mr-1" /> Back</Button>
          <Button :disabled="!demoSelections[exampleIndex]" @click="next()">
            {{ page === TOTAL_PAGES - 1 ? 'Start the task' : 'Continue' }} <i-fa6-solid-arrow-right class="ml-1" />
          </Button>
        </div>
      </template>

    </div>
  </ConstrainedTaskWindow>
</template>
