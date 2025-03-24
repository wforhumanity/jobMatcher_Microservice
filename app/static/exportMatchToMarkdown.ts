/**
 * Exports job match results to a well-formatted Markdown document
 * 
 * @param jobDescription - The raw job description text
 * @param matchResult - The job match result object containing score, strengths, gaps, actions, and summary
 * @returns A formatted Markdown string
 */
export interface MatchResult {
  score: number;
  strengths: string[];
  gaps: string[];
  actions: string[];
  summary: string;
}

export function exportMatchToMarkdown(
  jobDescription: string,
  matchResult: MatchResult
): string {
  // Create the title
  let markdown = `# Job Match Report\n\n`;

  // Add compatibility score section
  markdown += `## Compatibility Score\n\n${matchResult.score}\n\n`;

  // Add job description section
  markdown += `## Job Description\n\n\`\`\`\n${jobDescription}\n\`\`\`\n\n`;

  // Add strengths section
  markdown += `## Strengths\n\n`;
  matchResult.strengths.forEach(strength => {
    markdown += `* ${strength}\n`;
  });
  markdown += '\n';

  // Add gaps section
  markdown += `## Gaps\n\n`;
  matchResult.gaps.forEach(gap => {
    markdown += `* ${gap}\n`;
  });
  markdown += '\n';

  // Add recommended actions section
  markdown += `## Recommended Actions\n\n`;
  matchResult.actions.forEach((action, index) => {
    markdown += `${index + 1}. ${action}\n`;
  });
  markdown += '\n';

  // Add summary section
  markdown += `## Summary\n\n> ${matchResult.summary}\n`;

  return markdown;
}

// Example usage:
/*
const jobDescription = "Senior Frontend Developer...";
const matchResult = {
  score: 85,
  strengths: ["Strong React experience", "Team leadership"],
  gaps: ["No TypeScript exposure", "Limited cloud deployment experience"],
  actions: [
    "Take a TypeScript crash course",
    "Deploy a personal project using AWS",
    "Contribute to an open-source frontend repo"
  ],
  summary: "You're a great fit for this role! With just a few upgrades, you'll be even more competitive."
};

const markdown = exportMatchToMarkdown(jobDescription, matchResult);
console.log(markdown);
*/
