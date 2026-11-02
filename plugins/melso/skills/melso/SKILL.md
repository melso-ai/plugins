---
name: melso
description: "Connect Melso or work with the user's Melso company: invoices, expenses, income, tax returns and Gestiones. Use for Melso fiscal records and professional cases, not general tax advice unrelated to Melso."
---

# Work with Melso

Melso is a tax service for autónomos and empresas in Spain. This plugin uses
the remote fiscal MCP at `https://mcp.melso.ai/mcp` and the person's existing
Melso account. Follow the user's requested work and use only the tools and
actions that this connection lists.

## Connect and confirm the company

If the fiscal tools are missing or authentication fails, use the host's native
connection or reconnect flow for this plugin. The person signs in with Melso
OAuth and chooses one company; another company needs another connection.
Never request or display access tokens, passwords or certificate secrets.

Read `company` before working with records and confirm the selected company
with the user. Its kind must be `freelancer` (an autónomo) or `company` (an
empresa). If it is the wrong company, reconnect and select the intended one.
If the host still shows an old tool catalog, refresh the connection and start
a new conversation. Configuration alone is not a successful connection.

For a person without a Melso account, continue through signup from the OAuth
sign-in page. Preserve its return URL through signup and first-company setup
so they return to consent and then this client. Do not restart an unrelated
signup flow or invent a company ID.

When the request is only to install, connect or verify the plugin, report the
company and any remaining setup step, then stop. Use read-only calls for
connection checks; never create records, upload files or send messages as a
test.

If `company` reports pending onboarding, use the authenticated setup link
provided by Melso or guide the owner to the web app's setup for that company.
While setup is pending, only `company`, `fiscal_profile_read`, `fiscal_profile` and
`support_tickets_create` are listed. Companies are set up by the Melso team;
do not promise company self-signup. Without a plan that includes the tools,
record reads can remain available and a Gestión draft can still be saved.
Use the advertised action enums to determine what is available.


## Fiscal tool contracts and queries

When the person asks to merge duplicates, read both contacts and use
`contacts` `merge` with the duplicate's `source_id` and the chosen canonical
`target_id`. The target's name and populated fields win; missing data and both
roles are combined. Earlier identities remain aliases, so historical invoices,
income, expenses and new document intake still find the contact. The invoice's
legal contents and approved version stay unchanged. Retry with the same pair;
different nonempty fiscal identities must be corrected before merging.
`contacts` `delete` removes an unused contact; an invoice-linked contact must
be kept or merged. These operations are available tools: do not open a support
ticket or send the person to manual cleanup when they are listed.

Read actions of mixed families use the listed `*_read` tool: `contacts_read`,
`invoices_read`, `expenses_read`, `income_read`, `accounting_read`, `bank_read`,
`bank_statements_read`, `book_imports_read`, `gestiones_read` and
`fiscal_profile_read`. The base name lists change actions. Read-only families
such as `taxes` and `documents` keep their names. Use only the action enums
advertised to this connection; the server applies the same company, role and
plan gates to every call. Reading a version never authorizes changing it.

`invoices_read` and `expenses_read` `list` accept `q`, `document_number`,
`contact_id`, inclusive issue-date bounds `start_date`/`end_date`, due-date
bounds `due_date_start`/`due_date_end`, payment `status`, `sort`, `limit`
(1–200, default 50) and `cursor`. Sort by `date`, `due_date` or `total`, with
`-` for descending. `outstanding` means a positive recorded balance;
`overdue` also requires a due date before today in Europe/Madrid. `pending`,
`partial` and `completed` distinguish recorded settlements. Drafts, void
invoices and proformas are not outstanding debts. Expense due dates are the
saved maturities. Balances include reconciliations and confirmed invoice
payments; they do not prove a bank transfer.

Lists return summaries under `invoices` or `expenses`, `has_more` and
`next_cursor`. Follow every page needed to answer, retaining the same filters;
never call a partial page a complete total. Use `get` for full fiscal evidence
and the invoice version needed for issuance. Each action's JSON Schema carries
its required fields; structured results advertise their available output
contracts. A structured error provides `code`, `message`, optional `field`,
`retryable` and `next_action`. On version conflict, read again and obtain fresh
authorization. On an uncertain provider response, check the existing operation;
never create a replacement invoice or blindly retry a mutation.

## Records and documents

- `contacts`, `invoices`, `payments`, `expenses` and `income` work on this
  company's records. Follow each action's schema; amounts are EUR decimal
  strings. Read an existing record before updating it and pass its saved
  `version` as `expected_version` where required.
- `contacts` keeps the company's customers and suppliers with their tax ID,
  address, email, phone and a supplier's IBAN. Look a counterparty up with
  `list` before asking for its details, and save what the person tells you
  with `upsert`: with `id` only the fields given change; without it, a contact
  with the same tax ID is completed instead of duplicated. Reading a document
  with `from_document` saves its supplier or customer too.
- To record a supplier invoice or receipt, use `expenses` `upload`, PUT the
  requested file to the returned `upload_url` if this host can do so, then use
  `from_document`. Check `document_status` if processing is still pending.
  If the host cannot transfer the file, share the returned `web_upload_url`
  for the person to upload it in Melso. Do not claim a document was recorded
  until the tool confirms the resulting record.
- Create and save invoices with `invoices` `prepare`, for a customer from
  `contacts`. Ask only for missing customer, line-item or fiscal information
  and show the saved draft's totals.
  When the owner asks to issue that invoice and `issue` is listed, use its
  `id` and exact saved `version` as `expected_version`; no web visit is needed.
  Issuance uses Melso's configured service and may deliver the invoice through
  configured email. Do not issue or send when the request is only for a draft.
  Preserve the same invoice ID on retries; a changed version needs fresh
  authorization. Report registration, PDF and delivery from the returned
  states, not from a reserved invoice number. If `issue` is unavailable,
  `request_approval` returns the authenticated review page; say that this
  connection still requires web approval. Preparing a draft does not issue it.
  `payments` `mark_paid` records that an issued invoice was paid; it does not
  collect money or transfer funds.
- An expense or income covered by an approved or filed return cannot be
  deleted. Do not work around that restriction.

## Taxes and Gestiones

- Use `taxes` `calendar`, `list` and `get` for the available returns and
  deadlines. Describe the connected company's actual draft and state. An
  `is_preview` result is an estimate, not an approvable return. An `aeat_file`
  is an import file for preparation, not proof of filing.
- `taxes` `request_approval` returns the authenticated web review link. The
  customer authorizes the exact version in Melso; Melso's professionals then
  review and file an included return under the required authority. A changed
  version needs new approval. Filing is complete only with the external
  reference and receipt. No MCP tool approves, files or pays a tax return.
- `gestiones` `get` reads a case's conversation, versions, open information
  request and documents. Save a draft or submit it according to the user's
  request; `submit` sends work to the professional team and requires tax
  service coverage. Do not infer permission to submit from a request to draft.
- Use `message` with its idempotency key; `answer` must answer every item in
  the open request. For a version awaiting approval, use `message` with
  `changes: true` to request changes, or `request_approval` to share the
  authenticated review link. Neither action approves the version.
- For case attachments, use `upload`, PUT the file, then `upload_complete`;
  use its attachment ID in `create`, `message` or `answer`. Share the returned
  `web_upload_url` when the host cannot upload. `document_get` returns a case
  document as `content_base64`; only claim delivery if the host actually
  produces a usable file for the person.
- Cancel an unfiled case only after the person confirms; its history remains.
  Use `support_tickets_create` for a requested Melso support question or work
  that no listed tool covers, with `type: service_request` for service work.

Report what the tools confirmed, the resulting record or case and any review
link or missing information. Keep preparation, customer approval,
professional filing and receipt delivery as separate states.
