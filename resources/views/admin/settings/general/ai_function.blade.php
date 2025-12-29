<div class="tab-pane mt-3 fade" id="ai_function" role="tabpanel" aria-labelledby="ai_function-tab">
    <div class="row">
        <div class="col-12 col-md-6">
            <form action="{{ getAdminPanelUrl() }}/settings/main" method="post">
                {{ csrf_field() }}
                <input type="hidden" name="page" value="general">
                <input type="hidden" name="name" value="ai_function">

                <div class="form-group">
                    <label class="control-label">{{ trans('update.ai_provider') }}</label>
                    <select name="value[ai_provider]" class="form-control">
                        <option value="openai" {{ (!empty($itemValue) and $itemValue['ai_provider'] == 'openai') ? 'selected' : '' }}>OpenAI</option>
                        <option value="gemini" {{ (!empty($itemValue) and $itemValue['ai_provider'] == 'gemini') ? 'selected' : '' }}>Gemini</option>
                        <option value="deepseek" {{ (!empty($itemValue) and $itemValue['ai_provider'] == 'deepseek') ? 'selected' : '' }}>DeepSeek</option>
                    </select>
                </div>

                <div class="form-group">
                    <label class="control-label">{{ trans('update.openai_api_key') }}</label>
                    <input type="text" name="value[openai_api_key]" class="form-control"
                        value="{{ (!empty($itemValue) and !empty($itemValue['openai_api_key'])) ? $itemValue['openai_api_key'] : '' }}">
                </div>

                <div class="form-group">
                    <label class="control-label">{{ trans('update.gemini_api_key') }}</label>
                    <input type="text" name="value[gemini_api_key]" class="form-control"
                        value="{{ (!empty($itemValue) and !empty($itemValue['gemini_api_key'])) ? $itemValue['gemini_api_key'] : '' }}">
                </div>

                <div class="form-group">
                    <label class="control-label">{{ trans('update.deepseek_api_key') }}</label>
                    <input type="text" name="value[deepseek_api_key]" class="form-control"
                        value="{{ (!empty($itemValue) and !empty($itemValue['deepseek_api_key'])) ? $itemValue['deepseek_api_key'] : '' }}">
                </div>

                <button type="submit" class="btn btn-primary">{{ trans('admin/main.save_change') }}</button>
            </form>
        </div>
    </div>
</div>