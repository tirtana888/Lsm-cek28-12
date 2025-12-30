<?php

namespace App\Mixins\OpenAI;

use App\Enums\AiTextServices;
use App\Models\AiContent;
use OpenAI;
use App\Models\AiContentTemplate;

class AiContentGenerator
{

    public function makeContent($user, $data)
    {
        $makePrompt = $this->makePrompt($data);
        $prompt = $makePrompt['prompt'];
        $template = $makePrompt['template'];
        $language = $makePrompt['language'];
        $keyword = $makePrompt['keyword'];

        $result = [
            'text' => null,
            'images' => [],
        ];

        if ($data['service_type'] == "image") {
            $imageSize = $makePrompt['imageSize'];

            $result['images'] = $this->getImageContent($prompt, $imageSize);
        } else {
            $result['contents'] = $this->getTextContent($prompt);
        }

        $this->storeGeneratedContent($user, $data['service_type'], $result, $prompt, $template, $language, $keyword);

        return $result;
    }


    public function storeGeneratedContent($user, $serviceType, $result, $prompt, $template, $language = null, $keyword = null)
    {
        AiContent::query()->create([
            'user_id' => $user->id,
            'service_type' => $serviceType,
            'service_id' => !empty($template) ? $template->id : null,
            'keyword' => $keyword,
            'language' => $language,
            'prompt' => $prompt,
            'result' => json_encode($result),
            'created_at' => time(),
        ]);
    }

    private function getTextContent($prompt)
    {
        $contents = [];

        $aiSettings = getOthersPersonalizationSettings('ai_function');
        $provider = !empty($aiSettings) ? ($aiSettings['ai_provider'] ?? 'openai') : 'openai';

        if ($provider == 'gemini') {
            $contents = $this->getGeminiContent($prompt);
        } elseif ($provider == 'deepseek') {
            $contents = $this->getDeepSeekContent($prompt);
        } else {
            $contents = $this->getOpenAIContent($prompt);
        }

        return $contents;
    }

    private function getOpenAIContent($prompt)
    {
        $contents = [];
        $client = $this->makeOpenAIClient();

        $settings = getAiContentsSettingsName();
        $model = $settings['text_service_type'] ?? 'gpt-4o';
        $maxToken = $settings['max_tokens'] ?? null;
        $countText = !empty($settings['number_of_text_generated_per_request']) ? $settings['number_of_text_generated_per_request'] : 1;

        try {
            $result = $client->chat()->create([
                'model' => $model,
                'max_tokens' => isset($maxToken) ? (int) $maxToken : null,
                'n' => (int) $countText,
                'messages' => [
                    ["role" => "user", "content" => $prompt],
                ],
            ]);

            if (!empty($result['choices']) and count($result['choices'])) {
                foreach ($result['choices'] as $choice) {
                    if (!empty($choice['message']['content'])) {
                        $contents[] = $this->trimText($choice['message']['content']);
                    }
                }
            }

        } catch (\Exception $exception) {
            // Log or handle error
        }

        return $contents;
    }


    private function getGeminiContent($prompt)
    {
        $contents = [];
        $aiSettings = getOthersPersonalizationSettings('ai_function');
        $apiKey = $aiSettings['gemini_api_key'] ?? null;

        if (empty($apiKey)) {
            return $contents;
        }

        try {
            $client = new \GuzzleHttp\Client();
            $response = $client->post("https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={$apiKey}", [
                'json' => [
                    'contents' => [
                        [
                            'parts' => [
                                ['text' => $prompt]
                            ]
                        ]
                    ]
                ]
            ]);

            $result = json_decode($response->getBody()->getContents(), true);

            if (!empty($result['candidates'][0]['content']['parts'][0]['text'])) {
                $contents[] = $this->trimText($result['candidates'][0]['content']['parts'][0]['text']);
            }
        } catch (\Exception $e) {
            // Log or handle error
        }

        return $contents;
    }

    private function getDeepSeekContent($prompt)
    {
        $contents = [];
        $aiSettings = getOthersPersonalizationSettings('ai_function');
        $apiKey = $aiSettings['deepseek_api_key'] ?? null;

        if (empty($apiKey)) {
            return $contents;
        }

        try {
            $client = new \GuzzleHttp\Client();
            $response = $client->post("https://api.deepseek.com/v1/chat/completions", [
                'headers' => [
                    'Authorization' => "Bearer {$apiKey}",
                    'Content-Type' => 'application/json',
                ],
                'json' => [
                    'model' => 'deepseek-chat',
                    'messages' => [
                        ['role' => 'user', 'content' => $prompt]
                    ]
                ]
            ]);

            $result = json_decode($response->getBody()->getContents(), true);

            if (!empty($result['choices'][0]['message']['content'])) {
                $contents[] = $this->trimText($result['choices'][0]['message']['content']);
            }
        } catch (\Exception $e) {
            // Log or handle error
        }

        return $contents;
    }

    private function makeOpenAIClient()
    {
        $aiSettings = getOthersPersonalizationSettings('ai_function');
        $secretKey = $aiSettings['openai_api_key'] ?? null;

        // Fallback to old setting if new one is empty
        if (empty($secretKey)) {
            $settings = getAiContentsSettingsName();
            $secretKey = !empty($settings['secret_key']) ? $settings['secret_key'] : null;
        }

        if (!empty($secretKey)) {
            return OpenAI::factory()
                ->withApiKey($secretKey)
                ->make();
        }

        throw new \Exception("Invalid Api Key", "403");
    }

    private function trimText($text)
    {
        $text = ltrim($text, "\r\n");
        $text = ltrim($text, "\r");
        $text = ltrim($text, "\n\n");
        $text = ltrim($text, "\n");

        return ltrim($text, ".");
    }

    private function getImageContent($prompt, $imageSize = "256")
    {
        $client = $this->makeOpenAIClient();

        $settings = getAiContentsSettingsName();
        $maxImage = !empty($settings['number_of_images_generated_per_request']) ? $settings['number_of_images_generated_per_request'] : 1;

        $images = [];

        try {
            $result = $client->images()->create([
                'prompt' => $prompt,
                'n' => (int) $maxImage,
                'size' => $this->makeImageSize($imageSize),
                'response_format' => 'url',
            ]);

            if (!empty($result->data)) {
                foreach ($result->data as $datum) {
                    $images[] = $datum->url;
                }
            }
        } catch (\Exception $exception) {
            // Log or handle error
        }

        return $images;
    }

    private function makeImageSize($size)
    {
        $sizes = [
            '256' => '256x256',
            '512' => '512x512',
            '1024' => '1024x1024',
        ];

        return $sizes[$size] ?? '256x256';
    }


    private function makePrompt($data)
    {
        $prompt = null;
        $imageSize = null;
        $template = null;
        $language = null;
        $keyword = null;

        if ($data['service_type'] == "text" and $data['text_service_id'] == "custom_text") {
            $prompt = $data['question'];
        } else if ($data['service_type'] == "image" and $data['image_service_id'] == "custom_image") {
            $prompt = $data['image_question'];
            $imageSize = $data['image_size'];
        } else {
            $templateId = null;

            if (!empty($data['text_service_id'])) {
                $templateId = $data['text_service_id'];
            } else if (!empty($data['image_service_id'])) {
                $templateId = $data['image_service_id'];
            }

            $template = AiContentTemplate::query()->where('id', $templateId)
                ->where('enable', true)
                ->first();

            if (!empty($template)) {
                $prompt = $template->prompt;
                $language = $data['language'] ?? null;
                $keyword = $data['keyword'] ?? null;

                if ($data['service_type'] == "image") {
                    $keyword = $data['image_keyword'] ?? null;
                }

                if (!empty($language)) {
                    $lang = getLanguages($language);

                    if (!empty($lang) and !is_array($lang)) {
                        $language = $lang;
                    }
                }

                $height = !empty($data['length']) ? $data['length'] : ($template->enable_length ? $template->length : null);

                $prompt = str_replace("[language]", $language, $prompt);
                $prompt = str_replace("[keyword]", $keyword, $prompt);
                $prompt = str_replace("[length]", $height, $prompt);

                $imageSize = $template->image_size;
            }

        }


        return [
            'prompt' => $prompt,
            'imageSize' => $imageSize,
            'template' => $template,
            'language' => $language,
            'keyword' => $keyword,
        ];
    }

}
