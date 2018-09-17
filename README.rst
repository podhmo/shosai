shosai
========================================

.. image:: https://travis-ci.org/podhmo/shosai.svg?branch=master
    :target: https://travis-ci.org/podhmo/shosai

supporting tool, management stock type document(not flow type document).

config
----------------------------------------

please, setup $HOME/.config/shosai/config.json, like below.

.. code-block:: json

  {
    "docbase": {
      "teamname": "<team name>",
      "token": "<token>",
      "username": "<username>"
    },
    "hatena": {
      "blog_id": "<username>.hatenablog.com",
      "client_id": "<client id>",
      "client_secret": "<client secret>",
      "consumer_key": "<consumer key>",
      "consumer_secret": "<consumer secret>",
      "hatena_id": "<hatena id>",
    }
  }


push article
----------------------------------------

.. code-block:: console

  $ shosai docbase push docs/xxx.md

- upload (or update) article
- (the document has images `![text](url)`, uploading ones as attachment files)

pull article
----------------------------------------

.. code-block:: console

  $ shosai docbase pull docs/xxx.md

- update local article (using this command, when managed article is already downloaded)

clone article
----------------------------------------

.. code-block:: console

  $ shosai docbase clone https://<teamname>.docbase.io/posts/xxxxxx --name xxx.md


- download article

search article
----------------------------------------

.. code-block:: console

  $ shosai docbase search

- getting recently uploaded documents
