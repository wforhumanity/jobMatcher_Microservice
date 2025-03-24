/**
 * Exports job match results to a well-formatted Markdown document
 * 
 * @param {string} jobDescription - The raw job description text
 * @param {Object} matchResult - The job match result object
 * @param {number} matchResult.score - Compatibility score from 0-100
 * @param {string[]} matchResult.strengths - List of candidate's strengths
 * @param {string[]} matchResult.gaps - List of missing skills or qualifications
 * @param {string[]} matchResult.actions - List of actionable recommendations
 * @param {string} matchResult.summary - Motivational insight and summary
 * @returns {string} A formatted Markdown string
 */
function exportMatchToMarkdown(jobDescription, matchResult) {
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
