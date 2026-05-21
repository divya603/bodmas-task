export const QUIZ_QUESTIONS = [
  {
    id: 'pg1',
    questions: [
      {
        id: 'q1',
        question: 'What are you rating in this task?',
        multiSelect: false,
        answers: [
          "How correct the student's final answer is",
          "How well a belief statement matches the student's reasoning",
        ],
        correctAnswer: ["How well a belief statement matches the student's reasoning"],
      },
      {
        id: 'q2',
        question: 'What should your rating be based on?',
        multiSelect: false,
        answers: [
          "Whether the student got the correct final answer",
          "How well the belief statement matches the student's work",
        ],
        correctAnswer: ["How well the belief statement matches the student's work"],
      },
    ],
  },
]
