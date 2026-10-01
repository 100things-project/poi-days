// ============================================================
// お問い合わせフォーム2つを自動作成するスクリプト
//   ・POIGAME LAB お問い合わせ
//   ・POI DAYS お問い合わせ
//
// ★★★ 1回だけ実行してください ★★★
// （2回目以降に実行しても、新しいフォームは増やさず、
//   作成済みのURLを表示するだけにしてあります）
//
// 使い方: 関数「createContactForms」を選んで「実行」を押す。
// 結果は「実行ログ」に表示されます。
// ============================================================

// 送信後に表示するメッセージ（2つのフォーム共通）
var CONFIRMATION_MESSAGE =
  'お問い合わせありがとうございます。内容を確認のうえ、必要に応じてご連絡します。';

// メイン処理。この関数を実行します。
function createContactForms() {
  // 「プロパティ」= スクリプトに付けられるメモ帳。作成済みかどうかの記録に使います。
  var props = PropertiesService.getScriptProperties();

  // すでに作成済みなら、フォームを増やさずURLだけ表示して終了
  if (props.getProperty('FORMS_CREATED') === 'yes') {
    Logger.log('すでに作成済みです。新しいフォームは作りません。');
    logUrl_('POIGAME LAB お問い合わせ', props.getProperty('FORM1_ID'));
    logUrl_('POI DAYS お問い合わせ', props.getProperty('FORM2_ID'));
    return;
  }

  // ---------- フォーム1: POIGAME LAB ----------
  // FormApp.create() = 新しいGoogleフォームを作る命令
  var form1 = FormApp.create('POIGAME LAB お問い合わせ');
  form1.setDescription(
    'ポイ活ゲーム案件についてのご質問・情報提供・掲載依頼はこちらからどうぞ。返信にはお時間をいただく場合があります。'
  );
  form1.setConfirmationMessage(CONFIRMATION_MESSAGE);

  // 質問1: お名前（記述式・必須）
  form1.addTextItem()
    .setTitle('お名前(ニックネーム可)')
    .setHelpText('例:もち')
    .setRequired(true);

  // 質問2: メールアドレス（記述式・必須。メール形式かチェックする）
  addEmailQuestion_(form1);

  // 質問3: お問い合わせ種類（ラジオボタン・必須）
  // ラジオボタン = 選択肢から1つだけ選ぶ形式
  form1.addMultipleChoiceItem()
    .setTitle('お問い合わせ種類')
    .setChoiceValues([
      '掲載内容についての質問',
      '情報の誤り・更新のお知らせ',
      '掲載・広告のご依頼',
      'サイトへのご意見',
      'その他'
    ])
    .setRequired(true);

  // 質問4: 対象のゲーム名（記述式・任意）
  form1.addTextItem()
    .setTitle('対象のゲーム名')
    .setHelpText('例:放置少女')
    .setRequired(false);

  // 質問5: お問い合わせ内容（段落・必須）
  // 段落 = 長い文章を書ける入力欄
  form1.addParagraphTextItem()
    .setTitle('お問い合わせ内容')
    .setRequired(true);

  // ---------- フォーム2: POI DAYS ----------
  var form2 = FormApp.create('POI DAYS お問い合わせ');
  form2.setDescription(
    'ポイントサイトに関するご質問・ご感想・情報提供はこちらからどうぞ。'
  );
  form2.setConfirmationMessage(CONFIRMATION_MESSAGE);

  // 質問1: お名前（記述式・必須）
  form2.addTextItem()
    .setTitle('お名前(ニックネーム可)')
    .setHelpText('例:ゆき')
    .setRequired(true);

  // 質問2: メールアドレス（記述式・必須）
  addEmailQuestion_(form2);

  // 質問3: お問い合わせ種類（ラジオボタン・必須）
  form2.addMultipleChoiceItem()
    .setTitle('お問い合わせ種類')
    .setChoiceValues([
      '記事内容についての質問',
      '情報の誤り・更新のお知らせ',
      '取り上げてほしいポイントサイト・テーマ',
      'サイトへのご意見',
      'その他'
    ])
    .setRequired(true);

  // 質問4: お問い合わせ内容（段落・必須）
  form2.addParagraphTextItem()
    .setTitle('お問い合わせ内容')
    .setRequired(true);

  // ---------- 公開設定 ----------
  // 回答を受け付ける状態（公開）にする。
  // ※古い環境ではこの命令がないため、失敗しても止まらないようにしてあります。
  publish_(form1);
  publish_(form2);

  // ---------- 作成済みの記録を残す（2回目の実行で増えないように） ----------
  props.setProperty('FORM1_ID', form1.getId());
  props.setProperty('FORM2_ID', form2.getId());
  props.setProperty('FORMS_CREATED', 'yes');

  // ---------- URLをログに表示 ----------
  // 編集用URL = 自分が質問を直す画面 / 回答用URL = サイトに貼る公開リンク
  Logger.log('===== 作成完了 =====');
  Logger.log('【POIGAME LAB お問い合わせ】');
  Logger.log('編集用URL: ' + form1.getEditUrl());
  Logger.log('回答用URL(公開リンク): ' + form1.getPublishedUrl());
  Logger.log('【POI DAYS お問い合わせ】');
  Logger.log('編集用URL: ' + form2.getEditUrl());
  Logger.log('回答用URL(公開リンク): ' + form2.getPublishedUrl());
}

// メールアドレスの質問を追加する共通部品
function addEmailQuestion_(form) {
  // バリデーション = 入力内容のチェック（ここでは「メール形式か」を確認）
  var emailCheck = FormApp.createTextValidation()
    .setHelpText('メールアドレスの形式で入力してください。')
    .requireTextIsEmail()
    .build();

  form.addTextItem()
    .setTitle('メールアドレス')
    .setHelpText('返信用に使います')
    .setValidation(emailCheck)
    .setRequired(true);
}

// フォームを公開（回答受付）状態にする共通部品
function publish_(form) {
  try {
    form.setPublished(true);
  } catch (e) {
    // この命令が使えない環境では何もしない（最初から公開状態のため）
  }
  form.setAcceptingResponses(true);
}

// 作成済みフォームのURLを表示する共通部品（2回目の実行用）
function logUrl_(name, id) {
  if (!id) return;
  var form = FormApp.openById(id);
  Logger.log('【' + name + '】');
  Logger.log('編集用URL: ' + form.getEditUrl());
  Logger.log('回答用URL(公開リンク): ' + form.getPublishedUrl());
}
