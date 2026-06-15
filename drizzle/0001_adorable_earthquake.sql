CREATE TABLE `magic_links` (
	`id` int AUTO_INCREMENT NOT NULL,
	`studyId` int NOT NULL,
	`token` varchar(255) NOT NULL,
	`expiresAt` timestamp NOT NULL,
	`accessCount` int NOT NULL DEFAULT 0,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `magic_links_id` PRIMARY KEY(`id`),
	CONSTRAINT `magic_links_token_unique` UNIQUE(`token`)
);
--> statement-breakpoint
CREATE TABLE `medical_studies` (
	`id` int AUTO_INCREMENT NOT NULL,
	`userId` int NOT NULL,
	`fileName` varchar(255) NOT NULL,
	`fileType` varchar(50) NOT NULL,
	`originalImageUrl` text,
	`processedImageUrl` text,
	`status` enum('pending','processing','completed','failed') NOT NULL DEFAULT 'pending',
	`phase1Complete` int NOT NULL DEFAULT 0,
	`phase2Complete` int NOT NULL DEFAULT 0,
	`phase3Complete` int NOT NULL DEFAULT 0,
	`phase4Complete` int NOT NULL DEFAULT 0,
	`psnr` varchar(50),
	`ssim` varchar(50),
	`pseudonymizationHash` varchar(255),
	`detectedClasses` text,
	`boundingBoxes` text,
	`processingTimeMs` int,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `medical_studies_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
ALTER TABLE `magic_links` ADD CONSTRAINT `magic_links_studyId_medical_studies_id_fk` FOREIGN KEY (`studyId`) REFERENCES `medical_studies`(`id`) ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE `medical_studies` ADD CONSTRAINT `medical_studies_userId_users_id_fk` FOREIGN KEY (`userId`) REFERENCES `users`(`id`) ON DELETE no action ON UPDATE no action;