import { Message } from "../types/chat";

export const test_messages: Message[] = [
  {
    role: "user",
    content: "Who is Jesus?",
  },
  {
    role: "assistant",
    content:
      "Jesus Christ is the central figure of Christianity. Christians believe that He is the Son of God, the Messiah, and the Savior of humanity. The New Testament presents His life, teachings, death, and resurrection as central to the Christian faith.",
    sources: [
      {
        tool_name: "bible_search",
        tool_output:
          '[{"Index":27934,"book_name":"Romans","book_number":45,"chapter_number":1,"translation_name":"ENGLISHBBE","verse_number":4,"verse_text":"But was marked out as Son of God in power by the Holy Spirit through the coming to life again of the dead; Jesus Christ our Lord,"}]',
      },
    ],
  },

  {
    role: "user",
    content: "What did Jesus teach about loving others?",
  },
  {
    role: "assistant",
    content:
      "Jesus taught that love for others is one of the greatest commandments. He instructed His followers to love their neighbors and even to love their enemies. This love is presented as an active choice expressed through kindness, forgiveness, and selflessness.",
    sources: [
      {
        tool_name: "bible_search",
        tool_output:
          '[{"Index":25001,"book_name":"Matthew","book_number":40,"chapter_number":22,"translation_name":"ENGLISHBBE","verse_number":39,"verse_text":"And a second like it is this, Have love for your neighbour as for yourself."},{"Index":25120,"book_name":"Matthew","book_number":40,"chapter_number":5,"translation_name":"ENGLISHBBE","verse_number":44,"verse_text":"But I say to you, Have love for those who are against you, and make prayer for those who are cruel to you."}]',
      },
    ],
  },

  {
    role: "user",
    content: "Why is forgiveness important in Christianity?",
  },
  {
    role: "assistant",
    content:
      "Forgiveness is important because Christians are called to forgive others as they have received forgiveness from God. Jesus repeatedly emphasized reconciliation and mercy rather than holding on to resentment. Forgiveness does not mean that wrongdoing is ignored; rather, it reflects God's mercy and transforms how believers respond to those who hurt them.",
    sources: [
      {
        tool_name: "bible_search",
        tool_output:
          '[{"Index":25562,"book_name":"Matthew","book_number":40,"chapter_number":6,"translation_name":"ENGLISHBBE","verse_number":14,"verse_text":"For if you let men have forgiveness for their sins, you will have forgiveness from your Father in heaven."},{"Index":25563,"book_name":"Matthew","book_number":40,"chapter_number":6,"translation_name":"ENGLISHBBE","verse_number":15,"verse_text":"But if you do not forgive men, you will not have forgiveness from your Father for your sins."}]',
      },
    ],
  },
];
