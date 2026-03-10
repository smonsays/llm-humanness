<script setup>
import useAPI from '@/core/composables/useAPI'
const api = useAPI()

const estimatedTime = api.getConfig('estimated_time')
const payrate = api.getConfig('payrate')
</script>

<template>
  <div class="p-3 pt-2 text-left">
    <h1 class="text-3xl font-bold"><i-mdi-approve class="inline-block mr-2" />Informed Consent</h1>
    <hr class="mt-2 mb-3 h-px" />
    <p class="mb-4">
      You have been invited to take part in a research study designed to investigate human working memory capacity. It
      will be conducted by Professor Brenden M. Lake, principal investigator, at the Departments of Computer Science and
      Psychology at Princeton University. Your participation in this study is voluntary.
    </p>

    <h2 class="text-xl font-bold mt-4 mb-1">What will happen:</h2>
    <p class="mb-2">
      If you agree to participate, you will be asked to view tasks on a computer screen and make responses via mouse and
      keyboard. The study will take approximately {{ estimatedTime }} to complete. You will receive {{ payrate }} for your participation.
      At the end of the study, you will receive a written explanation (debriefing) describing its purpose in more
      detail.
    </p>
    <p class="mb-4">You must be 18 years or older and reside in the United States to participate.</p>

    <h2 class="text-xl font-bold mt-4 mb-1">Voluntary:</h2>
    <p class="mb-4">
      Taking part in this study is voluntary. If you choose to withdraw from the study after it has begun, your data will be deleted and thus not considered for analysis.
    </p>
    <h2 class="text-xl font-bold mt-4 mb-1">Risks and benefits:</h2>
    <p class="mb-4">
      There are no known risks associated with this study beyond those encountered in everyday life. You may not receive
      direct personal benefits from participating, but the study may help researchers better understand the working
      memory constraints of humans.
    </p>

    <h2 class="text-xl font-bold mt-4 mb-1">Confidentiality:</h2>
    <p class="mb-4">
      Your responses will be kept confidential. Your data will be linked only to your Prolific ID; we do not have access
      to your name or other identifying information. Data will be stored securely on our research servers and may be
      kept indefinitely for scientific purposes. We may share aggregated or anonymized data publicly. Any shared dataset
      will replace your Prolific ID with a randomly generated code.
    </p>

    <h2 class="text-xl font-bold mt-4 mb-1">Questions:</h2>
    <p class="mb-4">
      If you have questions about the study, you may contact the principal investigator, Brenden M. Lake at 35 Olden
      St., Princeton, NJ 08540,
      <a href="mailto:brenden@princeton.edu" class="text-blue-600 hover:underline">brenden@princeton.edu</a>. For
      questions about your rights as a research participant, you may contact Princeton’s Research Integrity and
      Assurance office, at
      <a href="mailto:ria@princeton.edu" class="text-blue-600 hover:underline">ria@princeton.edu</a> or 609-258-1252.
      The identifier of this study is: "Princeton University IRB #19196"
    </p>

    <p class="mt-6 italic text-gray-600">You may print or save a copy of this consent document for your records.</p>
  </div>
</template>
