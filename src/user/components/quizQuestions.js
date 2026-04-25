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
        question: "Is the student's working always visible when you answer the question?",
        multiSelect: false,
        answers: ['Yes', 'No'],
        correctAnswer: ['No'],
      },
    ],
  },
]
