-- CreateTable
CREATE TABLE "InterviewRecord" (
    "id" UUID NOT NULL,
    "applicationId" UUID NOT NULL,
    "round" INTEGER NOT NULL DEFAULT 1,
    "interviewType" TEXT NOT NULL DEFAULT 'technical',
    "scheduledAt" TIMESTAMP(3),
    "interviewer" TEXT,
    "duration" INTEGER,
    "content" TEXT,
    "feedback" TEXT,
    "rating" INTEGER,
    "result" TEXT,
    "notes" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "InterviewRecord_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "InterviewRecord_applicationId_idx" ON "InterviewRecord"("applicationId");

-- AddForeignKey
ALTER TABLE "InterviewRecord" ADD CONSTRAINT "InterviewRecord_applicationId_fkey" FOREIGN KEY ("applicationId") REFERENCES "Application"("id") ON DELETE CASCADE ON UPDATE CASCADE;
