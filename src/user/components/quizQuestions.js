export const QUIZ_QUESTIONS = [
  {
    id: 'pg1',
    questions: [
      {
        id: 'q1',
        question: 'Which describes the task you will do?',
        multiSelect: false,
        answers: [
          "Rate how accurate the student's math or reasoning is",
          "Rate how accurate a statement about the student's math or reasoning is",
        ],
        correctAnswer: ["Rate how accurate a statement about the student's math or reasoning is"],
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
