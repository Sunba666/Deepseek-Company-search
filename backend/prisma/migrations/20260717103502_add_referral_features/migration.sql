-- CreateTable
CREATE TABLE "ReferralFavorite" (
    "id" UUID NOT NULL,
    "userId" UUID NOT NULL,
    "referralId" UUID NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "ReferralFavorite_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ReferralRating" (
    "id" UUID NOT NULL,
    "userId" UUID NOT NULL,
    "referralId" UUID NOT NULL,
    "score" INTEGER NOT NULL DEFAULT 5,
    "comment" TEXT,
    "responseTime" TEXT,
    "isSuccess" BOOLEAN,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "ReferralRating_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ReferralReport" (
    "id" UUID NOT NULL,
    "userId" UUID NOT NULL,
    "referralId" UUID NOT NULL,
    "reason" TEXT NOT NULL,
    "detail" TEXT,
    "status" TEXT NOT NULL DEFAULT 'pending',
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "resolvedAt" TIMESTAMP(3),

    CONSTRAINT "ReferralReport_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "ReferralFavorite_userId_idx" ON "ReferralFavorite"("userId");

-- CreateIndex
CREATE INDEX "ReferralFavorite_referralId_idx" ON "ReferralFavorite"("referralId");

-- CreateIndex
CREATE UNIQUE INDEX "ReferralFavorite_userId_referralId_key" ON "ReferralFavorite"("userId", "referralId");

-- CreateIndex
CREATE INDEX "ReferralRating_referralId_idx" ON "ReferralRating"("referralId");

-- CreateIndex
CREATE UNIQUE INDEX "ReferralRating_userId_referralId_key" ON "ReferralRating"("userId", "referralId");

-- CreateIndex
CREATE INDEX "ReferralReport_referralId_idx" ON "ReferralReport"("referralId");

-- CreateIndex
CREATE INDEX "ReferralReport_status_idx" ON "ReferralReport"("status");

-- AddForeignKey
ALTER TABLE "ReferralFavorite" ADD CONSTRAINT "ReferralFavorite_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ReferralFavorite" ADD CONSTRAINT "ReferralFavorite_referralId_fkey" FOREIGN KEY ("referralId") REFERENCES "Referral"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ReferralRating" ADD CONSTRAINT "ReferralRating_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ReferralRating" ADD CONSTRAINT "ReferralRating_referralId_fkey" FOREIGN KEY ("referralId") REFERENCES "Referral"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ReferralReport" ADD CONSTRAINT "ReferralReport_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ReferralReport" ADD CONSTRAINT "ReferralReport_referralId_fkey" FOREIGN KEY ("referralId") REFERENCES "Referral"("id") ON DELETE CASCADE ON UPDATE CASCADE;
