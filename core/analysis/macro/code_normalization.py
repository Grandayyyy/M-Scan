
import re
import config.common as Config


class CodeNormalization:
    def __init__(self, _macro_code):
        """
        Initialization of object with macro code
        :param _macro_code: plain macro code passed
        """
        self.__macro_code__ = _macro_code

    def __remove_anomalies(self, macro_code=None):
        """
        This function remove new line, tabs, indentation of code and new line separator used in vba line. After removing
        these extra line of code it converts code into list.
        Function also remove vba meta information
        :param macro_code:
        :return: List of filtered macro code
        """
        if not macro_code:
            macro_code = self.__macro_code__

        macro_content = macro_code

        # Replace tab and new line with new line
        macro_content = macro_content.replace("\r\n", Config.LINE_SEPARATOR)
        macro_content = macro_content.replace(" _" + Config.LINE_SEPARATOR, " ")

        # Converted macro code strings into list
        macro_content_list = macro_content.split(Config.LINE_SEPARATOR)

        removed_whitespaces = []
        # Looping through macro code to ignore all whitespaces between macro code
        for vba_code_line in macro_content_list:
            vba_code_line = " ".join(vba_code_line.split())
            # Ignoring all whitespaces in macro code
            if vba_code_line == "":
                continue
            removed_whitespaces.append(vba_code_line)

        remove_meta = []
        for vba_code_line in removed_whitespaces:
            # Removing Attribute and ' from the code
            if vba_code_line.startswith("Attribute") or vba_code_line.startswith("'"):
                continue
            inline_comment_pos = vba_code_line.find(" '")
            if inline_comment_pos > -1:
                if vba_code_line.find('"', inline_comment_pos) < 0:
                    inline_comment_pos = inline_comment_pos
                    vba_code_line = vba_code_line[:inline_comment_pos]
            remove_meta.append(vba_code_line)

        remove_indentation = []
        # Removing line indentation from code
        for vba_code_line in remove_meta:
            vba_code_line = vba_code_line.replace('" & "', "")
            remove_indentation.append(vba_code_line)

        return remove_indentation

    @staticmethod
    def __extract_function(cleaned_code):
        """
        This function generate a dictionary from filtered macro code. It identify all function names and their
        corresponding function code. These extracted function names, codes dumped into dictionary.
        :param cleaned_code: filtered macro code
        :return: dictionary of function and their code
        """
        vba_functions = {}
        vba_function_code = False
        vba_function_name = ""
        for vba_code_line in cleaned_code:
            if " Lib " in vba_code_line and ' Alias ' in vba_code_line and not vba_function_code:
                if " Function " in vba_code_line:
                    vba_function_type = " Function "
                else:
                    vba_function_type = " Sub "

                function_name = vba_code_line[vba_code_line.find(vba_function_type) + len(
                    vba_function_type):vba_code_line.find(" Lib ")]
                os_function_name = vba_code_line[
                                   vba_code_line.find(" Alias \"") + len(" Alias \""):vba_code_line.find(
                                       "\" (",
                                       vba_code_line.find(" Alias \"") + len(" Alias \""))]
                vba_function_name = function_name

                if "libc.dylib" in vba_code_line:
                    vba_function_name += "(Mac)"
                vba_functions[vba_function_name] = "It's function calling windows's " + os_function_name
                continue

            if " Lib " in vba_code_line and not vba_function_code:
                if " Function " in vba_code_line:
                    vba_function_type = " Function "
                else:
                    vba_function_type = " Sub "

                vba_function_name = vba_code_line[vba_code_line.find(vba_function_type) + len(
                    vba_function_type):vba_code_line.find(" Lib ")]

                if "libc.dylib" in vba_code_line:
                    vba_function_name += "(Mac)"

                vba_functions[vba_function_name] = "It's custom defined function " + vba_function_name
                continue

            function_start_position = max(vba_code_line.find("Sub "), vba_code_line.find("Function "))
            function_start = False
            if vba_code_line.startswith("Sub") or vba_code_line.startswith("Function") or vba_code_line.startswith(
                    "Private") or vba_code_line.startswith("Public"):
                function_start = True

            function_end = vba_code_line.startswith("End Sub") or vba_code_line.startswith("End Function")
            if function_end:
                vba_function_code = False
                continue
            elif function_start and function_start_position > -1:
                vba_function_code = True
                if "Function " in vba_code_line:
                    vba_function_name = vba_code_line[
                                        (function_start_position + len("Function ")):vba_code_line.find("(")]
                elif "Sub " in vba_code_line:
                    vba_function_name = vba_code_line[(function_start_position + len("Sub ")):vba_code_line.find("(")]
                else:
                    pass
            elif vba_function_code:
                if vba_function_name in vba_functions:
                    vba_functions[vba_function_name] += Config.LINE_SEPARATOR + vba_code_line
                else:
                    vba_functions[vba_function_name] = vba_code_line
            else:
                pass
        return vba_functions

    @staticmethod
    def __extract_properties(cleaned_code):
        """
        This function extract properties from macro code, all found property names has corresponding code assigned in
        dictionary.
        :param cleaned_code: cleaned macro code from newline, tabs and meta information
        :return: dictionary of property and their code
        """
        vba_macro_property = {}
        is_property = False
        property_name = ""

        for vba_code_line in cleaned_code:
            property_start_position = max(vba_code_line.find("Property Let "), vba_code_line.find("Property Get "))
            property_end_position = vba_code_line.startswith("End Property")
            if property_end_position:
                is_property = False
                continue
            elif property_start_position > -1:
                is_property = True
                if "Property Let " in vba_code_line or "Property Get " in vba_code_line:
                    property_name = vba_code_line[(property_start_position + len("Property Let ")):vba_code_line.find(
                        "(")] + " (Property)"
                else:
                    pass
            elif is_property:
                if property_name in vba_macro_property:
                    vba_macro_property[property_name] += Config.LINE_SEPARATOR + vba_code_line
                else:
                    vba_macro_property[property_name] = vba_code_line
            else:
                pass
        return vba_macro_property

    @staticmethod
    def __check_key_combination(_function_code, _function_name):
        """
        Checks if a function contains code
        :param _function_code: dictionary of macro code
        :param _function_name: function name
        :return: boolean returned either function contains definition or not
        """
        try:
            if _function_code[_function_name]:
                return True
        except KeyError:
            return False

    def __generate_function_calls(self, macro_functions):
        """
        This function loop throw complete macro code, Function identify all function name and checks if function is
        called in from other defined functions. If a function is calling other function it add data into function
        dictionary.
        :param macro_functions: dictionary of cleaned function
        :return: dictionary of function calls
        """
        function_name_calls = []
        function_relation = {}
        for function_name in macro_functions:
            if function_name not in function_name_calls:
                function_name_calls.append(function_name)
                function_relation[function_name] = ''
        # analyze function calls
        for function_name in macro_functions:

            vba_function_code = macro_functions[function_name]
            function_count = list(filter(None, re.split('[\"(, \-!?:\r\n)&=.><]+', vba_function_code)))
            for inner_function_name in macro_functions:
                function_position = inner_function_name.find(" ")
                if function_position > -1:
                    inner_function_name = inner_function_name[:function_position]

                for function_index in range(0, function_count.count(inner_function_name)):
                    if function_name != inner_function_name:
                        if self.__check_key_combination(function_relation, function_name):
                            if inner_function_name not in function_relation[function_name]:
                                function_relation[function_name].append(inner_function_name)
                        else:
                            _function_name = [inner_function_name]
                            function_relation[function_name] = _function_name

        return function_relation

    @staticmethod
    def __extract_keywords(macro_functions):
        """
        This function extract known keywords from the macro code.
        :param macro_functions: dictionary of cleaned macro code
        :return: dictionary of found keywords
        """
        found_keywords = {}
        macro_content = macro_functions
        for vba_function_name in macro_content:
            function_keyword = []
            vba_function_code = macro_content[vba_function_name]
            vba_code_list = filter(None, re.split("\n", vba_function_code))
            sensitive_keywords = "(" + ")|(".join(Config.LIST_MALICIOUS_CASE_SENSITIVE) + ")"
            in_sensitive_keywords = "(" + ")|(".join(Config.LIST_MALICIOUS_CASE_INSENSITIVE) + ")"
            for vba_code_line in vba_code_list:
                sensitive_found_keywords = re.findall(sensitive_keywords, vba_code_line)
                in_sensitive_found_keywords = re.findall(in_sensitive_keywords, vba_code_line, re.IGNORECASE)
                all_keywords = sensitive_found_keywords + in_sensitive_found_keywords
                if all_keywords:
                    for this_match in all_keywords:
                        match_list = list(this_match)
                        for match_item in match_list:
                            if '' != match_item and match_item not in function_keyword:
                                function_keyword.append(match_item)
            found_keywords[vba_function_name] = function_keyword
        return found_keywords

    def __encode_escaping(self, container):
        """
        This function load data from json file and parse this data for creating dictionary. This dictionary contains
        all related information for web UI page.
        :param container: graph data from saved json
        :return: Tuple will be returned to caller First boolean / second dictionary
        boolean will be result of operation while second parameter will contain information related to sample.
        """
        function_calls = ''  # Function level variable to handle all function calls and custom strings for marmaid.js
        ui_javascript = ''  # This variable holds data related to vba and javascript code which will be displayed

        try:
            for function_name in container['function_calls']:
                for child_function in container['function_calls'][function_name]:
                    function_keywords = ''
                    style = ''
                    if child_function in container['keywords_macro']:
                        for suspicious_call in container['keywords_macro'][child_function]:

                            try:
                                if 'shell' in suspicious_call.lower() and self.__not_me('shell',
                                                                                        function_keywords):
                                    function_keywords = function_keywords + '<br/>' + 'fa:fa-bomb Shell Activity'
                                    style = 'style ' + child_function + ' fill:#20a8d8'
                                elif 'process' in suspicious_call.lower() and self.__not_me('process',
                                                                                            function_keywords):
                                    function_keywords = function_keywords + '<br>' + 'fa:fa-windows Process Activity'
                                    style = 'style ' + child_function + ' fill:#ffc107'

                                elif 'window' in suspicious_call.lower() and self.__not_me('window',
                                                                                           function_keywords):
                                    function_keywords = function_keywords + \
                                                        '<br>' + 'fa:fa-window-maximize Tweaking Windows'
                                elif 'download' in suspicious_call.lower() and self.__not_me('download',
                                                                                             function_keywords):
                                    function_keywords = function_keywords + '<br>' + \
                                                        'fa:fa-cloud-download-alt Downloading Something'
                                elif 'file' in suspicious_call.lower() and self.__not_me('file',
                                                                                         function_keywords):
                                    function_keywords = function_keywords + '<br>' + 'fa:fa-file File Operation'
                                elif 'application' in suspicious_call.lower() and self.__not_me(
                                        'application',
                                        function_keywords):
                                    function_keywords = function_keywords + '<br>' + 'fa:fa-magic Application Settings'
                            except:
                                pass
                        function_calls = function_calls + function_name + '[<b><center>' + function_name + \
                                         '</center> </b>]' + ' --> ' + child_function + '[<b><center>' \
                                         + child_function + '</center> </b>' + function_keywords + ']' + "\n" + style + '\n'

            if '' == function_calls:
                for function_name in container['function_calls']:
                    function_calls = function_calls + function_name + '[<b><center>' + function_name + \
                                     '</center> </b>]\n'

            for function_name in container['complete_code']:
                if '(' in function_name:
                    pass
                else:
                    function_calls = function_calls + 'click ' + function_name + ' ' + function_name + ' ' + \
                                     '"Click for details "' + "\n"
                    ui_javascript = ui_javascript + 'var ' + function_name + \
                                    ' = function(){ document.getElementById("code").innerHTML = "' + self.__escape(
                        (container['complete_code'][function_name]).replace('\n',
                                                                            '\\n')) + \
                                    '";$("#ex1").modal({ closeExisting: false}) }' + '\n'
                    # function_calls = function_calls + 'click ' + function_name + ' ' + function_name + ' ' + \
                    #                  '"Click for details "' + "\n"
                    # ui_javascript = ui_javascript + 'var ' + function_name + \
                    #                 ' = function(){ document.getElementById("code").innerHTML = "' + self.__escape(
                    #     (container['complete_code'][function_name]).replace('\n',
                    #                                                         '\\n')) + \
                    #                 '";$("#ex1").modal({ closeExisting: false}) }' + '\n'

        except:
            pass
        ui_data = {'function_calls': function_calls, 'javascript_code': ui_javascript}
        return ui_data

    @staticmethod
    def __not_me(keyword, ful_string):
        if keyword.lower() not in ful_string.lower():
            return True
        else:
            return False

    @staticmethod
    def __escape(macro_code):
        return macro_code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"',
                                                                                                  '&quot;').replace(
            "'", '&#39;')

    def do_normalization(self):
        """
        Function which performs calls to other defined function in class.
        :return: tuple return definition following,
            success
                boolean, dictionary of definition of keywords, function calls and relation between functions
            failure
                boolean, string of exception
        """
        cleaned_macro_code = self.__remove_anomalies()
        vba_functions = self.__extract_function(cleaned_macro_code)

        vba_function = vba_functions
        vba_properties = self.__extract_properties(cleaned_macro_code)

        vba_function.update(vba_properties)

        vba_function_calls = self.__generate_function_calls(vba_function)

        keywords = self.__extract_keywords(vba_function)

        _decoded_macro = {}
        try:
            _decoded_macro = {'function_calls': vba_function_calls, 'complete_code': vba_function,
                              'keywords_macro': keywords}
            ui_data = self.__encode_escaping(_decoded_macro)
            return True, ui_data
        except Exception as e:
            return False, 'Failed to normalize macro function. ' + str(e)
